from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0005_alter_mailing_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mailingattempt',
            old_name='attempted_at',
            new_name='attempt_time',
        ),
    ]

