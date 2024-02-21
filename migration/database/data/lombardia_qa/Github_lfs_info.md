# Info su Github Large File Storage

1) Installare da https://git-lfs.com/
1) Da linea di comando, nella cartella della repository:
    * git lfs install
    * git lfs track "*.csv"
    * git add path/to/file.csv
    * git lfs push --all origin my/branch
    * git push -u origin my/branch

    * git commit -m "add file.csv"
    * git push

** N.B. in caso di problemi: **
    - git filter-repo --> se lfs non funziona ed un file è rimasto bloccato in caricamento
    - git git lfs migrate --> per muovere un file nella glfs

** Per rimuovere glfs: **
    - git lfs uninstall
    - git lfs uninit