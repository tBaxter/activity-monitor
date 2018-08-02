# Generated by Django 2.0.7 on 2018-08-02 10:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('verb', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('override_string', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('target', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('actor_name', models.CharField(blank=True, editable=False, max_length=255, null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('actor', models.ForeignKey(on_delete='CASCADE', related_name='subject', to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete='CASCADE', to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'actions',
                'ordering': ['-timestamp'],
                'get_latest_by': 'timestamp',
            },
        ),
        migrations.AlterUniqueTogether(
            name='activity',
            unique_together={('content_type', 'object_id')},
        ),
    ]
