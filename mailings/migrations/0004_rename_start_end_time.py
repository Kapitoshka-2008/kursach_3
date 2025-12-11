from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0003_alter_mailing_status_alter_mailingattempt_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mailing',
            old_name='start_at',
            new_name='start_time',
        ),
        migrations.RenameField(
            model_name='mailing',
            old_name='end_at',
            new_name='end_time',
        ),
    ]

