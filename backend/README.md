# Hitas backend for City of Helsinki


## Prerequisites

* [Python 3.13](https://www.python.org/)
* [Poetry >= 1.3.0](https://github.com/python-poetry/poetry#installation)
* [Docker](https://docs.docker.com/get-docker/)
  * alternatively PostgreSQL 13

---

## Get the Development Environment Up and Running

1. Clone this repository
2. Enter the backend directory `cd hitas/backend`
3. Start the app by running `make docker-build`
4. Access Django admin from [localhost:8080/admin](http://localhost:8080/admin). Default username `hitas`/`hitas`


### Running development environment without Docker

* Create a database for this project
* Install Python requirements: `poetry install`
* Enable debug `echo 'DEBUG=True' >> .env` [And setup env variables](#environment-variables)
* Run `python manage.py migrate`
* Run `python manage.py runserver`
* Access Django admin from [localhost:8000/admin](http://localhost:8080/admin). Default username `hitas`/`hitas`


### Environment Variables

- Copy the template env file: `cp .env.template .env` and add values for the _placeholder_ variables in the `.env`
  file.


### Git blame ignore refs

Project includes a `.git-blame-ignore-revs` file for ignoring certain commits from `git blame`.
This can be useful for ignoring e.g. formatting commits, so that it is more clear from `git blame`
where the actual code change came from. Configure your git to use it for this project with the
following command:

```shell
git config blame.ignoreRevsFile .git-blame-ignore-revs
```

Git will now automatically look for the file when using `git blame`, no additional setup needed.


### Pre-commit hooks

* Pre-commit hooks are available for use in a local environment. They can be installed with
  `poetry run pre-commit install` and updated with `poetry run pre-commit autoupdate`.
* To skip running hooks during a commit, add a `--no-verify` flag to `git commit`.
* To run pre-commit on all files, use `poetry run pre-commit run --all-files`


### Testing

* Running the tests: `make tests`
* Running the tests without docker (local PostgreSQL required): `HITAS_TESTS_NO_DOCKER=1 make tests`


### API definitions

* It's possible to take a look into `openapi.yaml`
* After running `make docker-build` Swagger editor is running in [http://localhost:8090](http://localhost:8090)


### Helpful commands

* Opening a shell in the container: `docker-compose run --rm hitas bash`
* Running code formatting and linting: `make format`
* Make a initial database dump: `make dump`

---

## Setting up Tunnistamo for development


### Installing Tunnistamo

The setup requires Tunnistamo [git submodule] to be present, even though it is not used with the
remote setup. Initialize the git submodules with `git submodule update --init` and then
fetch the submodule with `git pull --recurse-submodules`.

Now make a local config for Tunnistamo docker compose:
```shell
cp tunnistamo/docker-compose.env.yaml.template tunnistamo/docker-compose.env.yaml
```

> In you code editor, you should exclude the `tunnistamo` folder from indexing, so that search and
> refactoring tools won't try to touch files this folder. For example in PyCharm this is done by
> right-clicking on the folder -> `Mark Directory as` -> `Excluded`.


### Using remote Tunnistamo backend

*This is the recommended way of proceeding*

> You'll need a Microsoft account linked to the Helsinki City Active Directory to use this method.
> If you are a developer for Hitas, you should be in the Active Directory.

Next you will need to get the **Tunnistamo Development Server Environment Variable Secret Key** and copy it to your
local development environment. You can get the secret key from the following path:
\
[Azure Pipelines] -> Pipelines -> Library -> `hitastj-api-development` -> `SOCIAL_AUTH_TUNNISTAMO_SECRET`
\
After copying the secret to your `backend/.env` should have these two lines:
```.dotenv
OIDC_API_ISSUER=https://tunnistamo.test.hel.ninja/openid
SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT=TUNNISTAMO_SECRET_KEY_GOES_HERE
```

Now after starting your backend server, you should now be able to log in using Tunnistamo at
`http://localhost:<port>/helauth/login`.
The `<port>` must be either 8080 or 8000.
Any other ports will not work, as these are the only ports configured on Tunnistamo's side.


### Using local Tunnistamo backend

> Currently, this only works if you run Hitas Backend locally. Docker setup has some networking
> problems which prevent requests from reaching the Tunnistamo container from Hitas backend container.

> If you are on Windows, you'll need to change the line-endings on `tunnistamo/manage.py`
> and `tunnistamo/docker-entrypoint.sh` to `LF`!


#### Creating your own OAuth app

Create a new OAuth app to GitHub. To do this, you should go to [Developer settings] -> OAuth Apps -> New OAuthApp.
Use what ever Application name, Homepage URL, and Application description you want.
Use http://localhost:8099/accounts/github/login/callback/ for the Authorization callback URL.
Create a new client secret for the app and copy it to somewhere safe.
Now, in `tunnistamo/docker-compose.env.yaml`, add `Client ID` and the `Client secret` from your
GitHub OAuth app to `SOCIAL_AUTH_GITHUB_KEY` and `SOCIAL_AUTH_GITHUB_SECRET` respectively.

You should be set up to re-run docker with `docker-compose --profile tunnistamo up --build --detach`
on the root level. This will build the Tunnistamo containers using the secrets you provided.
Tunnistamo admin interface will be running on `http://localhost:8099/admin`.


#### Configure the OIDC Provider Client in your local Tunnistamo

Log in using the username `admin` and password `admin`.
Modify the default `Project` client in `http://localhost:8099/admin/oidc_provider/client/` with
the following settings:

- Name: `Hitas`
- Redirect URIs: `http://localhost:8000/pysocial/complete/tunnistamo/`
  - *The URI port should be the same you are running your local backend at, e.g. 8000*
- Client ID: `hitas-django-admin-ui-dev`
  - Must match the `SOCIAL_AUTH_TUNNISTAMO_KEY` variable in `backend/.env`.


Change `OIDC_API_ISSUER` and `SOCIAL_AUTH_TUNNISTAMO_OIDC_ENDPOINT` to `http://localhost:8099/openid` in `backend/.env`.
Copy the `Client SECRET` to `SOCIAL_AUTH_TUNNISTAMO_SECRET` in `backend/.env`.

Remember to save the OIDC Provider Client!

Now start up your backend server on your local machine. You should now be able
to log in at `http://localhost:8000/helauth/login`.

[Tunnistamo]: https://github.com/City-of-Helsinki/tunnistamo
[git submodule]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
[Developer settings]: https://github.com/settings/developers
[Azure Pipelines]: https://dev.azure.com/City-of-Helsinki/hitastj
