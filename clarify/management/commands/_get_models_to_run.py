from collections import OrderedDict

from django.contrib.auth.models import User

from clarify.models import (
    UserProfile, Student, Site, Term, Section, SectionGradeLevels,
    EnrollmentRecord, StaffSectionRecord, DailyAttendanceNode,
    Gradebook, Category, Assignment, Score
)

models = OrderedDict({
    m.__name__.lower(): m for m in
    [User,
     UserProfile,
     Student,
     Site,
     Term,
     Section,
     SectionGradeLevels,
     EnrollmentRecord,
     StaffSectionRecord,
     DailyAttendanceNode,
     Gradebook,
     Category,
     Assignment,
     Score]
})


def get_models_to_run(options, none_if_empty=True):
    if not options["models"] and none_if_empty:
        return None
    if not options["models"]:
        return models.values()

    models_to_run = []

    for model_name in options["models"]:
        parsed = model_name.strip().lower()

        models_to_run += [models[parsed]]

    return models_to_run
