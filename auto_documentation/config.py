from dynaconf import Dynaconf

# Initialize Dynaconf
settings = Dynaconf(
    envvar_prefix="MD_PARSER",
    settings_files=['settings.yaml', '.secrets.yaml'],
    environments=True,
    load_dotenv=True,
)