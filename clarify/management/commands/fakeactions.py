from django.utils import timezone
from random import sample, randint, randrange
from tqdm import tqdm

from django.core.management.base import BaseCommand

from deltas.models import Action
from clarify.models import UserProfile, Student

START_DATE = timezone.datetime(2018, 9, 1, 0, 0, 0)
SILENT_MARKER = '\u200b'

NOTES = [('note', m) for m in [
    "Great job on today's quiz!",
    "Good work during small group work",
    "Had a rough start to class but worked through it",
    "Really loved the grit you showed through IP",
    "Not our best class today; lots of talking during IP",
    "Helped out after class, great to see"
]]

MESSAGES = [('message', m) for m in [
    "Texted mom about the bump in quiz score",
    "Texted home about some of the struggles during small group work today",
    "Texted brother the HW due for tomorrow, he'll help her with it",
    "Texted aunt regarding take home project, she'll be there to help",
]]

CALLS = [('call', m) for m in [
    "Called mom about absence, sick today",
    "Called home about the great work during groups, Dad loved it!",
    "Called gramma about missing lunch, says she'll bring tomorrow",
    "Left VM regarding last two missing HWs",
    "Left VM regarding 100 on the quiz!",
    "Left VM about Friday's test",
    "Called about study habits for the unit test, dad will assist",
]]

SAMPLES = NOTES + MESSAGES + CALLS


class Command(BaseCommand):
    help = "My shiny new management command."

    def add_arguments(self, parser):
        parser.add_argument('--unfake',
                            dest="unfake",
                            action="store_true")

    def handle(self, *args, **options):
        unfake = options["unfake"]
        if unfake:
            self.unfake()
        else:
            self.fake()

    def fake(self):
        profiles = UserProfile.objects.all()
        actions = []
        for profile in tqdm(profiles, desc="Users"):
            students = profile.get_enrolled_students()
            for student in tqdm(students[::7], desc="Students", leave=False):
                for _ in range(randint(0, 3)):
                    atype, note = sample(SAMPLES, 1)[0]
                    timestamp = self.random_date()
                    public = True if randint(0, 20) > 16 else False
                    actions.append(Action(
                        type=atype,
                        note=note + SILENT_MARKER,
                        created_by=profile,
                        student=student,
                        created_on=timestamp,
                        updated_on=timestamp,
                        completed_on=timestamp,
                        public=public
                    ))
        print("Bulk creating...")
        Action.objects.bulk_create(actions)

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(actions)} actions.'
        ))

    def unfake(self):
        actions = Action.objects.all()
        unfaked = 0
        for action in tqdm(actions,
                           desc="Unfaking actions",
                           leave=False):
            if action.note[-1] == SILENT_MARKER:
                action.delete()
                unfaked += 1
        self.stdout.write(self.style.SUCCESS(
            f'Deleted {unfaked} fake actions.'
        ))

    @staticmethod
    def random_date():
        """
        This function will return a random datetime between two datetime
        objects.
        """
        delta = timezone.now() - START_DATE
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = randrange(int_delta)
        return START_DATE + timezone.timedelta(seconds=random_second)