{pkgs, ...}: {
  env.DATABASE_URL = "postgres://admin:password@127.0.0.1:5432/test?sslmode=disable";

  packages = [pkgs.dbmate];

  languages.python = {
    enable = true;
    version = "3.11";
    poetry = {
      enable = true;
      activate.enable = true;
      install.enable = true;
    };
  };

  pre-commit.hooks = {
    alejandra.enable = true;
    black.enable = true;
    commitizen.enable = true;
    ruff.enable = true;
    shellcheck.enable = true;
    statix.enable = true;
    taplo.enable = true;
  };
}
