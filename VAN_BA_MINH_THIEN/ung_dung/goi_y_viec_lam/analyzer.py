import re
import unicodedata
from zipfile import ZipFile

from django.core.exceptions import ValidationError

from ung_dung.ho_so_sv.models import StudentSkill, Skill

MAX_PAGES = 15
MAX_EXTRACTED_CHARACTERS = 100_000
MAX_DOCX_UNPACKED_BYTES = 20 * 1024 * 1024

SKILL_ALIASES = {
    "Python": ("python",),
    "Django": ("django",),
    "Flask": ("flask",),
    "FastAPI": ("fastapi", "fast api"),
    "Java": ("java",),
    "JavaScript": ("javascript", "java script"),
    "TypeScript": ("typescript", "type script"),
    "C++": ("c++", "cpp"),
    "C#": ("c#", "c sharp"),
    "Go": ("golang",),
    "Rust": ("rust",),
    "PHP": ("php",),
    "Laravel": ("laravel",),
    "React": ("react", "reactjs", "react.js"),
    "Angular": ("angular", "angularjs"),
    "Vue.js": ("vue", "vuejs", "vue.js"),
    "HTML": ("html",),
    "CSS": ("css",),
    "SQL": ("sql",),
    "MySQL": ("mysql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "MongoDB": ("mongodb",),
    "Redis": ("redis",),
    "Git": ("git",),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "AWS": ("aws", "amazon web services"),
    "Azure": ("azure", "microsoft azure"),
    "Google Cloud": ("google cloud", "gcp"),
    "Linux": ("linux",),
    "Microsoft Excel": ("excel", "microsoft excel"),
    "Power BI": ("power bi",),
    "Tableau": ("tableau",),
    "Machine Learning": ("machine learning", "hoc may"),
    "Deep Learning": ("deep learning", "hoc sau"),
    "Data Analysis": ("data analysis", "phan tich du lieu"),
    "Figma": ("figma",),
    "Communication": ("communication", "giao tiep"),
    "Teamwork": ("teamwork", "lam viec nhom"),
    "Project Management": ("project management", "quan ly du an"),
}


def _normalize(value):
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value).strip()


def _extract_text(resume):
    extension = resume.original_name.rsplit(".", 1)[-1].casefold()
    try:
        with resume.file.open("rb") as file_obj:
            if extension == "pdf":
                from pypdf import PdfReader

                reader = PdfReader(file_obj, strict=False)
                if reader.is_encrypted:
                    raise ValidationError("CV PDF đang được đặt mật khẩu nên không thể phân tích.")
                if len(reader.pages) > MAX_PAGES:
                    raise ValidationError(f"Bản phân tích hiện giới hạn {MAX_PAGES} trang PDF.")
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            elif extension == "docx":
                from docx import Document

                with ZipFile(file_obj) as archive:
                    entries = archive.infolist()
                    if len(entries) > 1000 or sum(entry.file_size for entry in entries) > MAX_DOCX_UNPACKED_BYTES:
                        raise ValidationError("CV DOCX vượt giới hạn kích thước giải nén.")
                file_obj.seek(0)
                document = Document(file_obj)
                parts = [paragraph.text for paragraph in document.paragraphs]
                for table in document.tables:
                    for row in table.rows:
                        parts.append(" ".join(cell.text for cell in row.cells))
                text = "\n".join(parts)
            else:
                raise ValidationError("Chỉ hỗ trợ CV PDF hoặc DOCX.")
    except ValidationError:
        raise
    except ImportError as error:
        raise ValidationError("Thiếu thư viện đọc CV. Hãy cài các gói trong requirements.txt.") from error
    except Exception as error:
        raise ValidationError("Không đọc được CV. Hãy kiểm tra tệp PDF/DOCX có hợp lệ và không bị khóa.") from error

    text = text[:MAX_EXTRACTED_CHARACTERS]
    if not text.strip():
        raise ValidationError("Không tìm thấy văn bản trong CV. Có thể PDF là bản quét ảnh.")
    return text


def analyze_resume(resume, profile):
    text = _normalize(_extract_text(resume))
    vocabulary = {name: set(aliases) for name, aliases in SKILL_ALIASES.items()}
    for name in Skill.objects.order_by("name").values_list("name", flat=True)[:2000]:
        vocabulary.setdefault(name, set()).add(name)

    detected = []
    for name, aliases in vocabulary.items():
        normalized_aliases = sorted({_normalize(alias) for alias in aliases if _normalize(alias)}, key=len, reverse=True)
        if len(_normalize(name)) < 2:
            continue
        alternatives = "|".join(re.escape(alias) for alias in normalized_aliases)
        pattern = rf"(?<![\w+#])(?:{alternatives})(?![\w+#])"
        matches = list(re.finditer(pattern, text)) if alternatives else []
        occurrences = len(matches)
        matched_aliases = sorted({match.group(0) for match in matches})
        if occurrences:
            detected.append({"name": name, "occurrences": occurrences, "aliases": matched_aliases})
    detected.sort(key=lambda item: (-item["occurrences"], item["name"].casefold()))

    profile_skill_names = {
        _normalize(name) for name in
        profile.student_skills.select_related("skill").values_list("skill__name", flat=True)
    }
    for item in detected:
        item["already_in_profile"] = _normalize(item["name"]) in profile_skill_names
    detected_names = {_normalize(item["name"]) for item in detected}
    not_seen = [
        relation.skill.name
        for relation in profile.student_skills.select_related("skill").order_by("skill__name")
        if _normalize(relation.skill.name) not in detected_names
    ]
    incomplete_fields = [
        label for field, label in (
            ("full_name", "Họ tên"), ("school", "Trường học"),
            ("major", "Ngành học"), ("experience", "Kinh nghiệm"),
            ("bio", "Giới thiệu bản thân"),
        ) if not getattr(profile, field).strip()
    ]
    return {
        "detected_skills": detected,
        "profile_skills_not_found_in_cv": not_seen,
        "incomplete_fields": incomplete_fields,
        "method": "Từ điển kỹ năng và so khớp văn bản cục bộ; không dùng mô hình AI.",
    }


def add_detected_skills(profile, requested_names, analysis):
    canonical_names = {
        item["name"]: item["name"]
        for item in analysis["detected_skills"]
    }
    selected = set(requested_names) & set(canonical_names)
    added = 0
    for name in selected:
        skill, _ = Skill.objects.get_or_create(
            normalized_name=name.casefold(),
            defaults={"name": name},
        )
        _, created = StudentSkill.objects.get_or_create(
            student_profile=profile,
            skill=skill,
            defaults={"proficiency": StudentSkill.Proficiency.INTERMEDIATE},
        )
        added += int(created)
    return added
