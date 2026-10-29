import pandas as pd
from sklearn.preprocessing import StandardScaler

print("--- BẮT ĐẦU XỬ LÝ TOÀN BỘ DỮ LIỆU PAYSIM ---")

# 1. Đọc toàn bộ file dữ liệu (Bỏ tham số nrows để lấy tất cả các dòng)
print("Đang đọc dữ liệu")
df = pd.read_csv("data_table.csv")
print(f"Đã tải thành công! Tổng số giao dịch: {len(df):,}")

# 2. Xử lý các cột dạng chữ (Categorical columns) như 'type'
print("Đang mã hóa các loại giao dịch (type)...")
df = pd.get_dummies(df, columns=["type"], prefix="type")

# 3. Trích xuất và chuẩn hóa các đặc trưng quan trọng (Features)
features = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest']

# Bổ sung thêm các cột 'type' vừa được mã hóa one-hot
type_cols = [col for col in df.columns if col.startswith('type_')]
features.extend(type_cols)

print("Đang chuẩn hóa toàn bộ dữ liệu...")
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# Nhãn mục tiêu (Label): isFraud (1 là gian lận, 0 là bình thường)
y = df['isFraud'].values

print(f"Kích thước ma trận dữ liệu đầu vào X: {X.shape}")
print(f"Tổng số giao dịch gian lận trong toàn bộ tập dữ liệu: {y.sum():,}")
print("--- HOÀN TẤT XỬ LÝ TOÀN BỘ DỮ LIỆU ---")