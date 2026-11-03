from pathlib import Path
from zipfile import BadZipFile, ZipFile

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import Skill, StudentProfile, StudentResume, StudentSkill

MAX_RESUME_SIZE = 5 * 1024 * 1024
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class StudentProfileForm(forms.ModelForm):
    skills_text = forms.CharField(
        label="Kỹ năng",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="Nhập mỗi kỹ năng một dòng. Có thể ghi mức độ sau dấu hai chấm, ví dụ: Python: nâng cao.",
    )
    resume_file = forms.FileField(label="CV (PDF hoặc DOCX)", required=False)
    remove_resume = forms.BooleanField(label="Xóa CV hiện tại", required=False)

    class Meta:
        model = StudentProfile
        fields = (
            "full_name",
            "school",
            "major",
            "education",
            "experience",
            "bio",
            "location",
            "preferred_work_mode",
            "salary_min",
            "salary_max",
            "available_time",
            "is_searchable",
        )
        widgets = {
            "education": forms.Textarea(attrs={"rows": 3}),
            "experience": forms.Textarea(attrs={"rows": 4}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_searchable"].help_text = (
            "Mặc định tắt. Khi bật, nhà tuyển dụng có thể tìm thấy hồ sơ của bạn."
        )
        if self.instance and self.instance.pk:
            entries = []
            for relation in self.instance.student_skills.select_related("skill").all():
                level = dict(StudentSkill.Proficiency.choices)[relation.proficiency]
                entries.append(f"{relation.skill.name}: {level.lower()}")
            self.fields["skills_text"].initial = "\n".join(entries)

    def clean(self):
        cleaned = super().clean()
        minimum = cleaned.get("salary_min")
        maximum = cleaned.get("salary_max")
        if minimum is not None and maximum is not None and minimum > maximum:
            self.add_error("salary_max", "Lương tối đa phải lớn hơn hoặc bằng lương tối thiểu.")
        if cleaned.get("resume_file") and cleaned.get("remove_resume"):
            self.add_error("remove_resume", "Chọn tải CV mới hoặc xóa CV hiện tại.")
        return cleaned

    def clean_resume_file(self):
        uploaded = self.cleaned_data.get("resume_file")
        if not uploaded:
            return uploaded
        if uploaded.size > MAX_RESUME_SIZE:
            raise ValidationError("CV không được vượt quá 5 MB.")

        extension = Path(uploaded.name).suffix.lower()
        if extension not in {".pdf", ".docx"}:
            raise ValidationError("Chỉ chấp nhận tệp PDF hoặc DOCX.")

        header = uploaded.read(8)
        uploaded.seek(0)
        if extension == ".pdf" and not header.startswith(b"%PDF-"):
            raise ValidationError("Nội dung tệp không đúng định dạng PDF.")
        if extension == ".docx" and not header.startswith(b"PK\x03\x04"):
            raise ValidationError("Nội dung tệp không đúng định dạng DOCX.")
        if extension == ".docx":
            try:
                with ZipFile(uploaded) as archive:
                    valid_docx = {
                        "[Content_Types].xml",
                        "word/document.xml",
                    }.issubset(archive.namelist())
            except BadZipFile:
                valid_docx = False
            uploaded.seek(0)
            if not valid_docx:
                raise ValidationError("Tệp DOCX không hợp lệ.")
        return uploaded

    @transaction.atomic
    def save(self, user, commit=True):
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
            self.save_skills(profile)
            self.save_resume(profile)
        return profile

    def save_skills(self, profile):
        submitted = {}
        raw = self.cleaned_data.get("skills_text", "")
        levels = {
            "cơ bản": StudentSkill.Proficiency.BEGINNER,
            "beginner": StudentSkill.Proficiency.BEGINNER,
            "trung bình": StudentSkill.Proficiency.INTERMEDIATE,
            "intermediate": StudentSkill.Proficiency.INTERMEDIATE,
            "nâng cao": StudentSkill.Proficiency.ADVANCED,
            "advanced": StudentSkill.Proficiency.ADVANCED,
        }
        for line in raw.splitlines():
            if not line.strip():
                continue
            if ":" in line:
                name, level_text = line.rsplit(":", 1)
                proficiency = levels.get(level_text.strip().casefold())
                if proficiency is None:
                    raise ValidationError(
                        f"Mức độ kỹ năng không hợp lệ ở dòng: {line}. Dùng cơ bản, trung bình hoặc nâng cao."
                    )
            else:
                name = line
                proficiency = StudentSkill.Proficiency.INTERMEDIATE
            name = name.strip()
            if not name or len(name) > 100:
                raise ValidationError("Tên kỹ năng phải dài từ 1 đến 100 ký tự.")
            submitted[name.casefold()] = (name, proficiency)

        profile.student_skills.exclude(skill__normalized_name__in=submitted.keys()).delete()
        for normalized, (name, proficiency) in submitted.items():
            skill, _ = Skill.objects.get_or_create(
                normalized_name=normalized,
                defaults={"name": name},
            )
            StudentSkill.objects.update_or_create(
                student_profile=profile,
                skill=skill,
                defaults={"proficiency": proficiency},
            )

    def save_resume(self, profile):
        uploaded = self.cleaned_data.get("resume_file")
        remove = self.cleaned_data.get("remove_resume")
        current = profile.current_resume

        if remove and current:
            profile.current_resume = None
            profile.save(update_fields=("current_resume", "updated_at"))
            return

        if uploaded:
            resume = StudentResume.objects.create(
                student_profile=profile,
                original_name=Path(uploaded.name).name[:255],
                content_type=(
                    DOCX_MIME
                    if Path(uploaded.name).suffix.lower() == ".docx"
                    else "application/pdf"
                ),
                size_bytes=uploaded.size,
                file=uploaded,
            )
            profile.current_resume = resume
            profile.save(update_fields=("current_resume", "updated_at"))
