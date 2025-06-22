# To learn more about how to use Nix to configure your environment
# see: https://firebase.google.com/docs/studio/customize-workspace
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"

  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.postgresql_17
    pkgs.postgresql17Tools
    pkgs.git
  ];

  # Sets environment variables in the workspace
  env = {
    # PostgreSQL environment variables
    POSTGRES_USER = "your_db_user";
    POSTGRES_PASSWORD = "your_db_password";
    POSTGRES_DB = "ai_dev_bot";
    DATABASE_URL = "postgresql://your_db_user:your_db_password@localhost:5432/ai_dev_bot";
  };

  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
    ];

    # Enable previews
    previews = {
      enable = true;
      previews = {
        # web = {
        #   # Example: run "npm run dev" with PORT set to IDX's defined port for previews,
        #   # and show it in IDX's web preview panel
        #   command = ["npm" "run" "dev"];
        #   manager = "web";
        #   env = {
        #     # Environment variables to set for your server
        #     PORT = "$PORT";
        #   };
        # };
      };
    };

    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        # Initialize PostgreSQL database
        init-postgres = ''
          export PGDATA=${pkgs.postgresql_17}/share/postgresql-17
          initdb -D $PGDATA
          pg_ctl -D $PGDATA start
          createuser -s $POSTGRES_USER
          createdb -O $POSTGRES_USER $POSTGRES_DB
          psql -c "ALTER USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"
        '';
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Start PostgreSQL server
        start-postgres = ''
          export PGDATA=${pkgs.postgresql_17}/share/postgresql-17
          pg_ctl -D $PGDATA start
        '';
      };
    };
  };
}
