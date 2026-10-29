import re
import os
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

print("--- ĐANG KHỞI TẠO HỆ THỐNG PHÒNG THỦ TUYẾN ĐẦU (NLP & SEARCH AI) ---")

# 1. Cơ sở tri thức chuẩn hóa 16 kịch bản lừa đảo
fraud_knowledge_base = [
    {"id": "KB_01", "pattern": "Cơ quan công an tòa án viện kiểm sát gọi điện điều tra vụ án rửa tiền phong tỏa tài sản chuyển tiền vào tài khoản tạm giữ xác minh vô tội", "group": "Pháp luật / Bắt cóc"},
    {"id": "KB_14", "pattern": "Bắt cóc online yêu cầu học sinh sinh viên tự cách ly không liên lạc gia đình để chuyển tiền tống tiền", "group": "Pháp luật / Bắt cóc"},
    {"id": "KB_02", "pattern": "Người thân bạn bè gọi video cầu cứu bị tai nạn kẹt tiền gấp chuyển khoản vào số tài khoản lạ", "group": "Deepfake người thân"},
    {"id": "KB_03", "pattern": "Đầu tư tài chính quốc tế tiền số chứng khoán lợi nhuận khủng cam kết không thua lỗ nạp vốn rút phí bất thường", "group": "Đầu tư tài chính"},
    {"id": "KB_04", "pattern": "Tuyển cộng tác viên bấm like video đánh giá sản phẩm đơn hàng ảo nhận hoa hồng nạp tiền trước nhận lương sau", "group": "Cộng tác viên online"},
    {"id": "KB_05", "pattern": "Ngân hàng thông báo tài khoản bị khóa giao dịch bất thường bấm vào đường link lạ nhập mật khẩu mã OTP", "group": "Giả danh ngân hàng"},
    {"id": "KB_06", "pattern": "Mua bán online gửi ảnh biên lai chuyển khoản giả yêu cầu đặt cọc hoặc truy cập link nhận tiền", "group": "Gian lận thương mại"},
    {"id": "KB_07", "pattern": "Làm quen mạng xã hội hẹn hò xây dựng tình cảm viện lý do khó khăn chữa bệnh rủ đầu tư chung", "group": "Lừa tình cảm (Pig Butchering)"},
    {"id": "KB_08", "pattern": "Trúng thưởng điện thoại xe máy tiền thưởng đóng phí vận chuyển thuế trước bạ xác minh mở hồ sơ", "group": "Trúng thưởng giả"},
    {"id": "KB_09", "pattern": "Hướng dẫn cài ứng dụng giả dịch vụ công phần mềm điều khiển từ xa cấp quyền máy quét mã QR độc hại", "group": "Mã độc / App giả"},
    {"id": "KB_10", "pattern": "Thuê tài khoản ngân hàng cho thuê thẻ ATM nhận tiền hộ trả tiền công mã OTP", "group": "Rửa tiền / Thuê tài khoản"},
    {"id": "KB_11", "pattern": "Chuyển tiền nhầm yêu cầu hoàn trả sang tài khoản khác đòi nợ", "group": "Chuyển nhầm / Đòi nợ"},
    {"id": "KB_12", "pattern": "Giả danh luật sư công an chuyên gia thu hồi tiền lừa đảo yêu cầu đóng phí trước", "group": "Thu hồi tiền lừa đảo giả"},
    {"id": "KB_13", "pattern": "Quảng cáo cho vay online dễ dàng không thế chấp đóng phí hồ sơ giải ngân bảo đảm", "group": "Tín dụng đen / Cho vay giả"},
    {"id": "KB_16", "pattern": "Mời gửi tiết kiệm lãi suất cao bất thường chuyển tiền vào tài khoản cá nhân website giả mạo", "group": "Tiết kiệm lãi cao"}
]

# 2. Xử lý học đặc trưng văn bản (Fit TF-IDF Vectorizer trên kho tri thức)
kb_texts = [item["pattern"] for item in fraud_knowledge_base]
search_vectorizer = TfidfVectorizer(ngram_range=(1, 2))
kb_vectors = search_vectorizer.fit_transform(kb_texts)

# 3. Danh sách từ điển nhận diện tên các ngân hàng phổ biến tại Việt Nam
SUPPORTED_BANKS = {
    "vietcombank": "Vietcombank (VCB)", "vcb": "Vietcombank (VCB)",
    "techcombank": "Techcombank (TCB)", "tcb": "Techcombank (TCB)",
    "mbbank": "MB Bank", "mb bank": "MB Bank", "mb": "MB Bank",
    "bidv": "BIDV", "agribank": "Agribank", "acb": "ACB",
    "vpbank": "VPBank", "tpbank": "TPBank", "sacombank": "Sacombank",
    "eximbank": "Eximbank", "msb": "MSB", "ocb": "OCB",
    "shb": "SHB", "hdbank": "HDBank", "vietinbank": "VietinBank"
}

# 4. Hàm phân tích và đánh giá rủi ro tuyến đầu
def first_line_defense_system(message: str):
    msg_lower = message.lower()
    
    # --- BƯỚC 1: SEARCH AI (So khớp ngữ nghĩa) ---
    msg_vector = search_vectorizer.transform([message])
    similarities = cosine_similarity(msg_vector, kb_vectors)[0]
    best_match_idx = np.argmax(similarities)
    best_score = float(similarities[best_match_idx])
    
    matched_scenario = "An toàn"
    search_ai_score = 0.0
    if best_score > 0.12: 
        matched_scenario = fraud_knowledge_base[best_match_idx]["group"]
        search_ai_score = best_score * 100

    # --- BƯỚC 2: RULE-BASED & CƯỜNG ĐỘ TÂM LÝ ---
    risk_keywords = [
        'chuyển gấp', 'phong tỏa', 'tạm giữ', 'công an', 'nộp phí', 'mã otp', 
        'lợi nhuận khủng', 'không thua lỗ', 'nhiệm vụ', 'hoa hồng', 'link lạ', 
        'apk', 'điều khiển từ xa', 'thuê tài khoản', 'chuyển nhầm', 'thu hồi tiền', 
        'phí bảo hiểm', 'đặt cọc', 'trúng thưởng', 'lãi suất cao'
    ]
    keyword_hits = sum(1 for kw in risk_keywords if kw in msg_lower)
    rule_score = min(keyword_hits * 0.25, 1.0) * 100 

    urgency_words = ['gấp lắm', 'ngay lập tức', 'khẩn cấp', 'trong hôm nay', 'không được nói ai', 'tuyệt đối giữ bí mật', 'hết giờ']
    urgency_hits = sum(1 for uw in urgency_words if uw in msg_lower)
    if urgency_hits > 0:
        rule_score = min(rule_score * 1.3, 100.0)

    # --- BƯỚC 3: BÓC TÁCH THỰC THỂ ---
    detected_accounts = re.findall(r'\b\d{8,14}\b', message)
    detected_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
    detected_phones = re.findall(r'\b(?:\+84|0)(?:\d{9,10})\b', message)
    
    detected_banks = []
    for key, bank_name in SUPPORTED_BANKS.items():
        if key in msg_lower and bank_name not in detected_banks:
            detected_banks.append(bank_name)

    phishing_domains = ['-secure', '-login', '-verify', '-support', 'bank-', 'vcb-', 'techcom-', 'mbbank-']
    has_phishing_domain = any(domain in msg_lower for domain in phishing_domains)

    entity_penalty = 0.0
    if detected_accounts: entity_penalty += 30.0 
    if detected_phones: entity_penalty += 15.0   
    if detected_urls: entity_penalty += 35.0     
    if has_phishing_domain: entity_penalty += 25.0 

    # --- TỔNG HỢP ĐIỂM RỦI RO ---
    base_risk = max(search_ai_score, rule_score)
    final_risk_score = min(base_risk + entity_penalty, 100.0)
    is_threat = final_risk_score >= 40.0

    return {
        "risk_score": round(final_risk_score, 2),
        "is_scam": is_threat,
        "detected_scenario": matched_scenario if is_threat else "Không phát hiện kịch bản độc hại",
        "extracted_accounts": detected_accounts,
        "extracted_phones": detected_phones,
        "extracted_urls": detected_urls,
        "extracted_banks": detected_banks,
        "has_phishing_domain": has_phishing_domain,
        "warning_message": f"CẢNH BÁO: Phát hiện dấu hiệu thuộc nhóm [{matched_scenario}] giả mạo ngân hàng hoặc chứa thông tin đáng ngờ!" if is_threat else "Tin nhắn an toàn."
    }

# --- 5. LƯU MÔ HÌNH NLP RA FILE .pkl ĐỂ SẴN SÀNG GỌI TRONG MAIN ---
if __name__ == "__main__":
    model_filename = "nlp_model.pkl"
    model_data = {
        "vectorizer": search_vectorizer,
        "kb_vectors": kb_vectors,
        "knowledge_base": fraud_knowledge_base
    }

    with open(model_filename, "wb") as f:
        pickle.dump(model_data, f)
    print(f"✅ --- Đã lưu mô hình NLP thành công vào file '{model_filename}' ---")