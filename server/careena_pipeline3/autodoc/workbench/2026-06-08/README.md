Die hier vorhandenen Dateien sind Arbeitsdateien.

Sie sind alle KI generierte Dokumentation während des Entwicklungsprozesses, das heißt sie sind nicht universell wahr,
teilweise nicht auf ganz dem selben Stand (Zeitstempel beachten), aber geben einen groben überblick über den Entwicklungsstand.

Target Model 6 enthält eine relativ akkurate Architekturkarte, dafür wurde der Kern manuell freigelegt und periphere strukturen wie session, tooling etc explizit nicht abbildet.

Ich versuche hier noch kurz detaillierter zu beschreiben was das careena3 für features mitbringt:

- einen eigenen simulation runner für testing (im frontend /simrun im chat eingeben, dauert aktuell allerdings ne ganze ganze weile)

- umfassenderes logging. aktuell gibt es zwei logs, einmal für die pipeline, einen für den verlauf der simulation
    - beim serverneustart werden alte log files zeitgestempelt ins archiv verschoben und frische logfiles angelegt

- die logik im chat ist aktuell etwas hakelig, teilweise sind da hardcodierte antworten drin, die logik dahinter steht noch nicht ganz, genauso wie der call 3 der antworten soll.
 da müsste dann einiges aus dem master prompt wieder rein denke ich
    - genaueres dazu in current weaknesses, das ist auch eine der aktuellsten dateien. (auch hier, größere problembereiche stimmen wahrscheinlich, spezfische probleme kann aber muss nicht)
