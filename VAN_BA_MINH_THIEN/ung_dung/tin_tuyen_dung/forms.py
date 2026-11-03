from django import forms
from django.db.models import F, Q
from django.utils import timezone

from ung_dung.ho_so_sv.models import Skill, StudentSkill

from .models import Job, JobCategory, JobSkill


class JobForm(forms.ModelForm):
    skills_text = forms.CharField(
        label="Kỹ năng yêu cầu",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Nhập mỗi kỹ năng một dòng; có thể ghi mức độ sau dấu hai chấm (cơ bản, trung bình, nâng cao).",
    )

    class Meta:
        model = Job
        fields = (
            "title",
            "category",
            "description",
            "requirements",
            "location",
            "work_mode",
            "employment_type",
            "salary_min",
            "salary_max",
            "deadline",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "requirements": forms.Textarea(attrs={"rows": 5}),
            "location": forms.TextInput(
                attrs={"list": "vn-provinces", "autocomplete": "address-level1"}
            ),
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = JobCategory.objects.filter(is_active=True)
        if self.instance and self.instance.pk:
            self.fields["skills_text"].initial = "\n".join(
                f"{relation.skill.name}: {dict(StudentSkill.Proficiency.choices)[relation.required_level].lower()}"
                for relation in self.instance.job_skills.select_related("skill")
            )

    def clean(self):
        cleaned = super().clean()
        salary_min = cleaned.get("salary_min")
        salary_max = cleaned.get("salary_max")
        if salary_min is not None and salary_max is not None and salary_min > salary_max:
            self.add_error("salary_max", "Lương tối đa phải lớn hơn hoặc bằng lương tối thiểu.")
        deadline = cleaned.get("deadline")
        if deadline and deadline < timezone.localdate():
            self.add_error("deadline", "Hạn ứng tuyển phải từ hôm nay trở đi.")
        self.skill_entries = self.parse_skills(cleaned.get("skills_text", ""))
        return cleaned

    def parse_skills(self, text):
        levels = {
            "cơ bản": StudentSkill.Proficiency.BEGINNER,
            "beginner": StudentSkill.Proficiency.BEGINNER,
            "trung bình": StudentSkill.Proficiency.INTERMEDIATE,
            "intermediate": StudentSkill.Proficiency.INTERMEDIATE,
            "nâng cao": StudentSkill.Proficiency.ADVANCED,
            "advanced": StudentSkill.Proficiency.ADVANCED,
        }
        entries = {}
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                name, level_text = line.rsplit(":", 1)
                level = levels.get(level_text.strip().casefold())
                if level is None:
                    self.add_error(
                        "skills_text",
                        f"Mức độ kỹ năng không hợp lệ ở dòng ‘{line}’. Dùng cơ bản, trung bình hoặc nâng cao.",
                    )
                    continue
            else:
                name, level = line, StudentSkill.Proficiency.INTERMEDIATE
            name = name.strip()
            if not name or len(name) > 100:
                self.add_error("skills_text", "Tên kỹ năng phải dài từ 1 đến 100 ký tự.")
                continue
            entries[name.casefold()] = (name, level)
        return entries

    def save_skills(self, job):
        entries = getattr(self, "skill_entries", {})
        job.job_skills.exclude(skill__normalized_name__in=entries.keys()).delete()
        for normalized, (name, level) in entries.items():
            skill, _ = Skill.objects.get_or_create(
                normalized_name=normalized,
                defaults={"name": name},
            )
            JobSkill.objects.update_or_create(
                job=job,
                skill=skill,
                defaults={"required_level": level, "is_required": True},
            )


class JobSearchForm(forms.Form):
    SORT_CHOICES = (
        ("newest", "Mới nhất"),
        ("deadline", "Hạn ứng tuyển gần nhất"),
        ("salary_high", "Lương cao trước"),
    )

    keyword = forms.CharField(label="Từ khóa", required=False, max_length=100)
    category = forms.ModelChoiceField(
        label="Danh mục",
        queryset=JobCategory.objects.none(),
        required=False,
        empty_label="Tất cả danh mục",
    )
    location = forms.CharField(
        label="Địa điểm",
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={"list": "vn-provinces", "autocomplete": "address-level1"}
        ),
    )
    work_mode = forms.ChoiceField(
        label="Hình thức",
        required=False,
        choices=[("", "Tất cả hình thức"), *Job.WorkMode.choices],
    )
    employment_type = forms.ChoiceField(
        label="Loại công việc",
        required=False,
        choices=[("", "Tất cả loại công việc"), *Job.EmploymentType.choices],
    )
    salary_min = forms.IntegerField(label="Lương từ", required=False, min_value=0)
    salary_max = forms.IntegerField(label="Lương đến", required=False, min_value=0)
    sort = forms.ChoiceField(label="Sắp xếp", choices=SORT_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = JobCategory.objects.filter(is_active=True)

    def clean(self):
        cleaned = super().clean()
        minimum = cleaned.get("salary_min")
        maximum = cleaned.get("salary_max")
        if minimum is not None and maximum is not None and minimum > maximum:
            self.add_error("salary_max", "Mức lương đến phải lớn hơn hoặc bằng mức lương từ.")
        return cleaned

    def apply(self, queryset):
        if not self.is_valid():
            return queryset
        data = self.cleaned_data
        keyword = data.get("keyword", "").strip()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(requirements__icontains=keyword)
                | Q(employer__organization_name__icontains=keyword)
            )
        if data.get("category"):
            queryset = queryset.filter(category=data["category"])
        if data.get("location"):
            queryset = queryset.filter(location__icontains=data["location"].strip())
        if data.get("work_mode"):
            queryset = queryset.filter(work_mode=data["work_mode"])
        if data.get("employment_type"):
            queryset = queryset.filter(employment_type=data["employment_type"])
        if data.get("salary_min") is not None:
            queryset = queryset.filter(
                Q(salary_max__gte=data["salary_min"]) | Q(salary_max__isnull=True)
            )
        if data.get("salary_max") is not None:
            queryset = queryset.filter(
                Q(salary_min__lte=data["salary_max"]) | Q(salary_min__isnull=True)
            )

        sort = data.get("sort") or "newest"
        if sort == "deadline":
            return queryset.order_by("deadline", "-created_at")
        if sort == "salary_high":
            return queryset.order_by(F("salary_max").desc(nulls_last=True), "-created_at")
        return queryset.order_by("-created_at")
