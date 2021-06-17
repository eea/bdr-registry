# Generated by Django 2.2.24 on 2021-06-17 11:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bdr_registry', '0006_accountuniquetoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='company', to='bdr_registry.Account'),
        ),
        migrations.AlterField(
            model_name='company',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='bdr_registry.Country'),
        ),
        migrations.AlterField(
            model_name='company',
            name='obligation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='companies', to='bdr_registry.Obligation'),
        ),
        migrations.AlterField(
            model_name='companynamehistory',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='namehistory', to='bdr_registry.Company'),
        ),
        migrations.AlterField(
            model_name='companynamehistory',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='nextaccountid',
            name='obligation',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='bdr_registry.Obligation'),
        ),
        migrations.AlterField(
            model_name='obligation',
            name='email_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='post_office.EmailTemplate'),
        ),
        migrations.AlterField(
            model_name='person',
            name='account',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='person', to='bdr_registry.Account'),
        ),
        migrations.AlterField(
            model_name='reportingstatus',
            name='reporting_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reporting_statuses', to='bdr_registry.ReportingYear'),
        ),
        migrations.AlterField(
            model_name='siteconfiguration',
            name='self_register_email_template',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='post_office.EmailTemplate'),
        ),
    ]