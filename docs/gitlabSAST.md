# Adding Static Application Security Tests (SAST) provided by Gitlab

Gitlab provides set of SAST that are easy to include in your project. [Link to Gitlab docs](https://docs.gitlab.com/ee/user/application_security/sast/)

## From Gitlab docs

For GitLab 11.9 and later, to enable SAST you must include the SAST.gitlab-ci.yml template provided as a part of your GitLab installation. For GitLab versions earlier than 11.9, you can copy and use the job as defined that template.

Try it by adding following to your ``.gitlab-ci.yml`` file:
``` yaml
include:
  - template: Security/SAST.gitlab-ci.yml
```
The included template creates SAST jobs in your CI/CD pipeline and scans your project’s source code for possible vulnerabilities.

The results are saved as a SAST report artifact that you can later download and analyze. Due to implementation limitations, we always take the latest SAST artifact available.
