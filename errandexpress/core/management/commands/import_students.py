import csv
from django.core.management.base import BaseCommand
from core.models import EnrolledStudent

class Command(BaseCommand):
    help = 'Imports enrolled students from a CSV file (student_id, full_name, course)'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        try:
            with open(csv_file, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                created_count = 0
                updated_count = 0
                
                for row in reader:
                    student_id = row.get('student_id')
                    full_name = row.get('full_name', '')
                    course = row.get('course', '')
                    
                    if not student_id or "NAN TOTAL NAN" in full_name or "NAN FEMALE NAN" in full_name or "NAN MALE NAN" in full_name:
                        continue
                        
                    student, created = EnrolledStudent.objects.update_or_create(
                        student_id=student_id,
                        defaults={
                            'full_name': full_name,
                            'course': course
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                        
                self.stdout.write(self.style.SUCCESS(f'Successfully imported students. Created: {created_count}, Updated: {updated_count}'))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
