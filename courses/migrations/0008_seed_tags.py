from django.db import migrations

TAGS = [
    ("Python",           "python"),
    ("JavaScript",       "javascript"),
    ("Web Development",  "web-development"),
    ("Django",           "django"),
    ("Machine Learning", "machine-learning"),
    ("Data Science",     "data-science"),
    ("React",            "react"),
    ("Database",         "database"),
    ("Mobile Dev",       "mobile-dev"),
    ("DevOps",           "devops"),
    ("Cooking",          "cooking"),
    ("Art",              "art"),
]

def seed_tags(apps, schema_editor):
    Tag = apps.get_model("courses", "Tag")
    for name, slug in TAGS:
        Tag.objects.get_or_create(name=name, slug=slug)

def unseed_tags(apps, schema_editor):
    Tag = apps.get_model("courses", "Tag")
    Tag.objects.filter(slug__in=[slug for _, slug in TAGS]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("courses", "0007_tag_course_difficulty_course_is_free_course_language_and_more"),  # ← change this to your latest migration
    ]

    operations = [
        migrations.RunPython(seed_tags, unseed_tags),
    ]
