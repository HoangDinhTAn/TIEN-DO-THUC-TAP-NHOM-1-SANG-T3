import torch
import torch.nn as nn
import torch.optim as optim
from torch_geometric.nn import GCNConv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np

print("--- [BƯỚC 1] KHỞI TẠO VÀ XÂY DỰNG ĐỒ THỊ PAYSIM CHO GNN ---")

# Import ma trận đặc trưng X và nhãn y đã được tiền xử lý chuẩn từ file DataPaysim.py
from DataPaysim import X, y

# Đọc file dữ liệu gốc để trích xuất quan hệ tài khoản (nameOrig -> nameDest) tạo đồ thị mạng lưới
df = pd.read_csv("data_table.csv")

num_nodes = X.shape[0]
x_tensor = torch.tensor(X, dtype=torch.float32)
y_tensor = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

# Xây dựng ma trận kề đồ thị (Edge Index) mô phỏng dòng tiền luân chuyển giữa các tài khoản
print("Đang ánh xạ dòng tiền và xây dựng không gian Topo mạng lưới (Edge Index)...")
edge_index_list = []
limit_rows = min(num_nodes, len(df))

for i in range(limit_rows - 1):
    # Tạo kết nối đồ thị 2 chiều (bidirectional) giữa các giao dịch liên tiếp trong luồng dòng tiền
    edge_index_list.append([i, i + 1])
    edge_index_list.append([i + 1, i])

edge_index = torch.tensor(edge_index_list, dtype=torch.long).t().contiguous()

# Chia tập Train / Test có phân tầng (Stratify) giữ tỷ lệ gian lận chuẩn xác
indices = np.arange(num_nodes)
train_indices, test_indices = train_test_split(indices, test_size=0.2, random_state=42, stratify=y)

train_mask = torch.zeros(num_nodes, dtype=torch.bool)
test_mask = torch.zeros(num_nodes, dtype=torch.bool)
train_mask[train_indices] = True
test_mask[test_indices] = True

# Tính toán hệ số pos_weight để xử lý triệt để bài toán mất cân bằng dữ liệu PaySim (phạt nặng khi bỏ sót gian lận)
num_neg = (y_tensor[train_mask] == 0).sum().float()
num_pos = (y_tensor[train_mask] == 1).sum().float()
pos_weight = num_neg / num_pos if num_pos > 0 else torch.tensor(1.0)

print(f"Tổng số nút giao dịch trên đồ thị: {num_nodes:,}")
print(f"Số lượng mẫu Train: {train_mask.sum().item():,}")
print(f"Số lượng mẫu Test: {test_mask.sum().item():,}")
print(f"Hệ số trọng số phạt gian lận (pos_weight): {pos_weight:.2f}")

# --- [BƯỚC 2] XÂY DỰNG KIẾN TRÚC MẠNG NƠ-RON ĐỒ THỊ GCN (Graph Convolutional Network) ---
class FraudGNN(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        super(FraudGNN, self).__init__()
        # Tầng tích chập đồ thị thứ 1: Tổng hợp thông tin từ hàng xóm (Neighborhood Aggregation)
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        
        # Tầng tích chập đồ thị thứ 2: Nâng cao cấu trúc biểu diễn không gian ẩn (Embedding)
        self.conv2 = GCNConv(hidden_channels, 16)
        
        # Lớp đầu ra Linear kết hợp Sigmoid bóp méo xác suất gian lận từ 0 đến 1
        self.out_layer = nn.Linear(16, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = self.relu(x)
        x = self.dropout(x)
        x = self.conv2(x, edge_index)
        x = self.relu(x)
        x = self.out_layer(x)
        return self.sigmoid(x)

# Khởi tạo mô hình với số chiều đầu vào in_channels khớp hoàn toàn với số cột của ma trận X
in_features_dim = X.shape[1]
model = FraudGNN(in_channels=in_features_dim, hidden_channels=32)
optimizer = optim.Adam(model.parameters(), lr=0.01, weight_decay=5e-4)

# --- [BƯỚC 3] VÒNG LẶP HUẤN LUYỆN (TRAINING LOOP) ---
epochs = 10
print(f"\n--- [BƯỚC 3] ĐANG TIẾN HÀNH HUẤN LUYỆN MÔ HÌNH GNN TRÊN TOÀN ĐỒ THỊ ({epochs} Epochs) ---")
model.train()

for epoch in range(epochs):
    optimizer.zero_grad()
    
    # Forward Pass qua toàn bộ đồ thị mạng lưới (Message Passing)
    out = model(x_tensor, edge_index)
    preds = out[train_mask]
    targets = y_tensor[train_mask]
    
    # Tính Binary Cross Entropy Loss có nhân hệ số pos_weight để ép mô hình học cách bắt gian lận
    loss = -torch.mean(
        targets * torch.log(torch.clamp(preds, min=1e-9)) * pos_weight + 
        (1 - targets) * torch.log(torch.clamp(1 - preds, min=1e-9))
    )
    
    loss.backward()
    optimizer.step()
    
    print(f"Epoch [{epoch+1}/{epochs}] - Loss: {loss.item():.4f}")

# Lưu lại file trọng số mô hình GNN hoàn chỉnh
torch.save(model.state_dict(), "HlmhGNN.pth")
print("✅ --- HUẤN LUYỆN GNN HOÀN TẤT! Đã lưu trọng số vào file 'HlmhGNN.pth' thành công ---")

# --- [BƯỚC 4] ĐÁNH GIÁ HIỆU SUẤT TRÊN TẬP TEST ---
print("\n--- [BƯỚC 4] ĐÁNH GIÁ MÔ HÌNH GNN TRÊN TẬP TEST ---")
model.eval()

with torch.no_grad():
    test_out = model(x_tensor, edge_index)
    test_predictions = (test_out[test_mask] >= 0.5).float()
    
    y_pred_np = test_predictions.cpu().numpy()
    y_true_np = y_tensor[test_mask].cpu().numpy()

correct = (test_predictions == y_tensor[test_mask]).sum().item()
total = test_mask.sum().item()
accuracy = correct / total

print(f"Tổng số mẫu test: {total:,}")
print(f"Độ chính xác tổng thể (Accuracy): {accuracy * 100:.4f}%")

print("\n--- BÁO CÁO CHI TIẾT HIỆU SUẤT GNN (CLASSIFICATION REPORT) ---")
print(classification_report(y_true_np, y_pred_np, target_names=["Bình thường (0)", "Gian lận (1)"], zero_division=0))

print("Ma trận nhầm lẫn (Confusion Matrix):")
print(confusion_matrix(y_true_np, y_pred_np))
print("--- HOÀN TẤT TOÀN BỘ QUY TRÌNH HUẤN LUYỆN ---")