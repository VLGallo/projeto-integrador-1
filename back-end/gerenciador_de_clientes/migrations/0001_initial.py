# Generated by Django 5.0.3 on 2024-03-27 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="GerenciadorDeClientes",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("nome", models.CharField(max_length=200)),
                ("telefone", models.CharField(max_length=30)),
                ("endereco", models.CharField(max_length=200)),
                ("email", models.EmailField(max_length=254)),
            ],
        ),
    ]
