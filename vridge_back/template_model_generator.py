import json, os
from pathlib import Path

#    ( )
INPUT_SPEC = Path("api_traffic.har")    #  Path("openapi.json")
OUTPUT_DIR = Path("migrations_from_spec_template"); OUTPUT_DIR.mkdir(exist_ok=True)

#  HAR   (   )
if not INPUT_SPEC.exists():
    print(f" {INPUT_SPEC}    HAR  ...")
    sample_har = {
        "log": {
            "entries": [
                {
                    "request": {
                        "url": "https://videoplanet.up.railway.app/api/video-planning/list/",
                        "method": "GET"
                    },
                    "response": {
                        "content": {
                            "text": json.dumps({
                                "data": {
                                    "id": 1,
                                    "title": "Sample Video Planning",
                                    "description": "A sample video planning description that is longer than 255 characters to test the TextField vs CharField logic. This should be long enough to trigger the TextField creation instead of CharField.",
                                    "is_active": True,
                                    "view_count": 100,
                                    "rating": 4.5,
                                    "tags": ["video", "planning", "sample"],
                                    "metadata": {"key": "value"},
                                    "created_at": "2023-12-07T10:00:00Z"
                                }
                            })
                        }
                    }
                },
                {
                    "request": {
                        "url": "https://videoplanet.up.railway.app/api/projects/list/",
                        "method": "GET"
                    },
                    "response": {
                        "content": {
                            "text": json.dumps({
                                "data": {
                                    "id": 1,
                                    "name": "Sample Project",
                                    "manager": "Project Manager",
                                    "is_public": True,
                                    "budget": 50000,
                                    "completion_rate": 0.75,
                                    "team_members": ["Alice", "Bob", "Charlie"],
                                    "settings": {"theme": "dark", "notifications": True}
                                }
                            })
                        }
                    }
                },
                {
                    "request": {
                        "url": "https://videoplanet.up.railway.app/api/feedbacks/create/",
                        "method": "POST"
                    },
                    "response": {
                        "content": {
                            "text": json.dumps({
                                "data": {
                                    "id": 1,
                                    "title": "Feedback Title",
                                    "content": "Feedback content",
                                    "is_resolved": False,
                                    "priority": 3,
                                    "score": 8.5,
                                    "attachments": [],
                                    "reviewer_data": {"name": "John Doe"}
                                }
                            })
                        }
                    }
                }
            ]
        }
    }
    INPUT_SPEC.write_text(json.dumps(sample_har, indent=2))
    print(f"  HAR  : {INPUT_SPEC}")

try:
    # 1) HAR 
    har = json.loads(INPUT_SPEC.read_text())

    # 2) · 
    models = {}
    for e in har["log"]["entries"]:
        url = e["request"]["url"]
        if "/api/" not in url: continue
        base = url.split("/api/")[-1].strip("/").split("/")[0]
        name = base.rstrip("s").title()
        body = {}
        try:
            body = json.loads(e["response"]["content"]["text"])
        except: continue
        data = body.get("data", body)
        if isinstance(data, dict):
            fields = {}
            for k,v in data.items():
                if isinstance(v, bool): tp="models.BooleanField()"
                elif isinstance(v, int): tp="models.IntegerField()"
                elif isinstance(v, float): tp="models.FloatField()"
                elif isinstance(v, str) and len(v)>255: tp="models.TextField()"
                elif isinstance(v, str): tp="models.CharField(max_length=255)"
                elif isinstance(v, list): tp="models.JSONField()"
                else: tp="models.JSONField()"
                fields[k] = tp
            if fields: models[name] = fields

    # 3) models.py 
    models_py = Path("app_template/models_from_spec.py")
    models_py.parent.mkdir(exist_ok=True)
    models_py.write_text("from django.db import models\n\n" + "\n\n".join(
        ["class %s(models.Model):\n%s\n    def __str__(self): return str(self.pk)" %
         (name, "\n".join(f"    {k} = {ft}" for k,ft in flds.items()))
         for name,flds in models.items()]
    ))

    # 4)   
    i=1
    for name,flds in models.items():
        mig = f"""# Generated migration for {name}
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="{name}",
            fields=[
                ('id', models.AutoField(primary_key=True)),
"""
        for k,ft in flds.items():
            mig += f"                ('{k}', {ft}),\n"
        mig += """            ],
        ),
    ]
"""
        Path(OUTPUT_DIR/f"{i:04d}_create_{name.lower()}.py").write_text(mig)
        i+=1

    print(" Django      ( )")
    print(f"  : {len(models)}")
    print(f"  : {models_py}")
    print(f"  : {OUTPUT_DIR}")

except Exception as e:
    print(f"    : {e}")