from django.db import models
from django_resized import ResizedImageField


class InstitutionSupportedSemester(models.Model):
    admin_list_filter = ("id", "institution", "semester")

    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)
    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.institution} {self.semester}"


class Institution(models.Model):
    admin_search_fields = ("id", "full_name", "nickname")

    full_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50)
    inst_logo = ResizedImageField(
        "Institution Logo",
        upload_to="institution_logos",
        size=[200, 200],
        quality=100,
        keep_meta=False,
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.nickname}({self.full_name})"


class Department(models.Model):
    admin_search_fields = ("id", "full_name", "nickname")
    admin_list_filter = ("institution",)

    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.nickname}({self.full_name}) of {self.institution.nickname}"


class Semester(models.Model):
    code = models.IntegerField()

    def __str__(self):
        return str(self.code)


class ScrapeTarget(models.Model):
    admin_search_fields = (
        "id",
        "institution__full_name",
        "institution__nickname",
        "semester__code",
    )
    admin_list_filter = ("institution", "semester")

    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)
    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["institution", "semester"], name="unique_scrape_target"
            ),
        ]

    def __str__(self):
        return f"{self.institution.full_name} {self.semester.code}"


class Course(models.Model):
    admin_search_fields = ("id", "name", "course_code")
    admin_list_filter = ("institution",)

    name = models.CharField(max_length=255)
    course_code = models.CharField(max_length=32)
    credits = models.IntegerField()
    institution = models.ForeignKey("Institution", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course_code}({self.credits}) {self.name[:20]}..."


class OpenedCourse(models.Model):
    admin_search_fields = ("id", "course__course_code", "course__name")
    admin_list_filter = ("semester",)

    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)
    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    notes = models.CharField(max_length=600, blank=True)


class Section(models.Model):
    admin_search_fields = ("id", "course__name", "section_code")

    course = models.ForeignKey("Course", on_delete=models.CASCADE)
    section_code = models.CharField(max_length=32)

    def __str__(self):
        return f"{self.section_code}"


class OpenedSection(models.Model):
    admin_search_fields = ("id", "section__section_code")
    admin_list_filter = ("semester",)

    semester = models.ForeignKey("Semester", on_delete=models.CASCADE)
    section = models.ForeignKey("Section", on_delete=models.CASCADE)
    seats = models.IntegerField("Number of total seats open", blank=True, null=True)
    open_seats = models.IntegerField(
        "Number of open seats currently", blank=True, null=True
    )
    waitlist = models.IntegerField(
        "Number of people on waitlist with higher priority", blank=True, null=True
    )
    holdfile = models.IntegerField(
        "Number of people on waitlist with lower priority", blank=True, null=True
    )

    def __str__(self):
        return f"{self.section} at {self.semester}"


class Instructor(models.Model):
    admin_search_fields = ("id", "name")

    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Teach(models.Model):
    admin_search_fields = (
        "id",
        "instructor__name",
        "opened_section__section__section_code",
    )
    admin_list_filter = ("opened_section__semester",)

    instructor = models.ForeignKey("Instructor", on_delete=models.CASCADE)
    opened_section = models.ForeignKey("OpenedSection", on_delete=models.CASCADE)


class Building(models.Model):
    admin_search_fields = ("id", "nickname", "full_name")

    full_name = models.CharField("Full Name", max_length=255, blank=True)
    nickname = models.CharField("Short Name", max_length=127)

    def __str__(self) -> str:
        return f"{self.nickname}"


class Location(models.Model):
    admin_search_fields = ("id", "room", "building__nickname")

    room = models.CharField(max_length=32, blank=True)
    building = models.ForeignKey("Building", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.building} {self.room}"


class Duration(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} to {self.end_time}"


class Day(models.Model):
    day = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.day}"


class Meeting(models.Model):
    admin_search_fields = (
        "id",
        "opened_section__section__section_code",
        "location__room",
        "location__building__nickname",
    )
    admin_list_filter = ("day", "opened_section__semester")

    duration = models.ForeignKey("Duration", on_delete=models.CASCADE)
    day = models.ForeignKey("Day", on_delete=models.CASCADE)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)
    opened_section = models.ForeignKey("OpenedSection", on_delete=models.CASCADE)
