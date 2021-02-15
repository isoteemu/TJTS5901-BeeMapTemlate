# Localization in Flask

You can find translations being implemented on propaedeutic video at 1:15:00 mark. <https://moodle.jyu.fi/mod/hvp/view.php?id=462788>. Whole localization setup is in i18n branch of reference implementation.

## Quickstart

- Add localization support using [flask-babel](https://flask-babel.tkte.ch/) into your application. It provides [gettex](https://en.wikipedia.org/wiki/Gettext) compatible functions. Remember to add it also in `requirements.txt`! See 275b20e4
- Use translation functions in templates (145c3681) and in code.
- Extract strings from templates and from code using pybabel: `$ pybabel extract -F babel.cfg -o messages.pot .`
- Generate locale specific translations using pybabel `$ pybabel init -i messages.pot -d translations -l fi`
  **OR** if you have already done initial, update existing translations with new strings from `.pot` -file: `$ pybabel update -i messages.pot -d translations`
- Translate generated file `translations/fi/LC_MESSAGES.po`
- Compile translations into gettex compatible format `$ pybabel compile -d translations`
- Add tests. Reference test can be found at `tests/test_app.py` which is implemented at e5224849
- Add compilation into a pipeline. You should not upload pot files in version control, as person doing translations might not be familiar with development workflows.

## Adding into pipeline

If using alpine based images (example `image: google/cloud-sdk:alpine`), add `apk update -q`, `apk add py3-pip` and replace `pip3` with `pip`. Reference implementation uses debian based images (`python:3` and `google/cloud-sdk`).

Edit `.gitlab-ci.yml` and add into job descritions `script` section before deployment or running tests `- pybabel compile -d translations`. If using separate artifact store and build stage it should be sufficient to add it there. But in reference implementation compilation is done in every stage separately.

As example, deployment job might look like:
```yaml
deploy:
  stage: deploy
  environment:
    name: production
  image: google/cloud-sdk
  script:
  # Install pybabel
  - pip3 install flask-babel --prefer-binary
  # Compile translations
  - pybabel compile -d translations

  - gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
  - cp $GOOGLE_APPLICATION_CREDENTIALS appcredentials.json
  # Copy config file
  - cp $INSTANCE_CONFIG_PRODUCTION instance_config.py
  - gcloud --quiet --project $PROJECT_ID app deploy app.yaml

  only:
    - master
```
