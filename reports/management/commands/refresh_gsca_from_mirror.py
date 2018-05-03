import pytz
from django.core.management.base import BaseCommand, CommandError
from sis_pull.models import GradebookSectionCourseAffinity, Section, Gradebook, \
    Staff, Course
from sis_mirror.models import GradebookSectionCourseAff
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Rebuilds sis_pull GradebookSectionCourseAffinity from sis_mirror'

    def handle(self, *args, **options):
        affinities = []
        for aff in tqdm(GradebookSectionCourseAff.objects.all(), desc="GSCA"):
            gradebook_id = Gradebook.objects.\
                get(source_object_id=aff.gradebook_id).id
            section_id = Section.objects.\
                get(source_object_id=aff.section_id).id
            course_id = Course.objects.\
                get(source_object_id=aff.course_id).id
            user_id = Staff.objects.\
                get(source_object_id=aff.user_id).user.id

            created = pytz.utc.localize(aff.created) if aff.created else None
            modified = pytz.utc.localize(aff.modified) if aff.modified else None

            affinities.append(GradebookSectionCourseAffinity(
                gradebook_id=gradebook_id,
                section_id=section_id,
                course_id=course_id,
                user_id=user_id,
                created=created,
                modified=modified
            ))

        GradebookSectionCourseAffinity.objects.bulk_create(affinities)

        self.stdout.write(self.style.SUCCESS(
            'Built new GradebookSectionCourseAffinity models'
        ))