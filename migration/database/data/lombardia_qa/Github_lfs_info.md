# Info su Github Large File Storage
E' un programma da installare, che viene usato insieme a git per gestire dei puntatori ai file più grandi di 100MB, fino a 2GB. Permette a git di farci accedere ai files in modo diverso, ma a noi non cambia nulla ed una volta configurato funziona tutto allo stesso modo.

1) Installare da https://git-lfs.com/
1) Da linea di comando, nella cartella della repository:
    * git lfs install
    * git lfs track "*.csv" --> bisogna sempre configurare il tipo di files che vogliamo aggiungere

    * git add path/to/file.csv
    * git lfs push --all origin my/branch
    * git push -u origin my/branch

    * git commit -m "add file.csv"
    * git push

Tutti i collaboratori devono installare Github Large File Storage per accedere ai file, 
però solo la prima persona che carica il file deve configurare GLFS per gestirlo.

** N.B. in caso di problemi: **
    - git filter-repo --> se lfs non funziona ed un file è rimasto bloccato in caricamento
    - git lfs migrate --> per muovere un file nella lfs

** Per rimuovere glfs: **
    - git lfs uninstall
    - git lfs uninit