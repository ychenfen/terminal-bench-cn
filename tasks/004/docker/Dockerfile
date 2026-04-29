FROM python:3.11-slim
WORKDIR /work
RUN pip install --no-cache-dir "Django==4.2.*"

RUN django-admin startproject blog . \
    && python manage.py startapp articles \
    && python manage.py startapp comments \
    && python manage.py startapp core

# Wire core/articles/comments into INSTALLED_APPS
RUN python -c "import re,pathlib; p=pathlib.Path('blog/settings.py'); s=p.read_text(); s=s.replace('INSTALLED_APPS = [', \"INSTALLED_APPS = [\\n    'core',\\n    'articles',\\n    'comments',\"); p.write_text(s)"

# Minimal models in articles/comments
RUN cat <<'EOF' > articles/models.py
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField()
EOF

RUN cat <<'EOF' > comments/models.py
from django.db import models


class Comment(models.Model):
    article_id = models.IntegerField()
    body = models.TextField()
EOF

# Empty core/models.py — agent will fill it
RUN echo "from django.db import models  # noqa: F401" > core/models.py

CMD ["bash"]
