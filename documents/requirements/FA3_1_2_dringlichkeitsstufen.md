# FA3.1.2 Dokumentation der Dringlichkeitsstufen

## Zweck

Diese Dokumentation definiert die Bedeutung der Dringlichkeitsstufen innerhalb der Anwendung. Ziel ist eine einheitliche Verwendung der Begriffe in Regeln, Tests, Backend-Ausgaben und Versorgungsempfehlungen.

Die Dringlichkeitsstufen dienen nicht der klinischen Triage im Sinne einer Notaufnahme. Die Anwendung entscheidet nicht, wie schnell eine Person medizinisch behandelt werden muss, und ersetzt keine ärztliche Einschätzung. Stattdessen dienen die Stufen als sicherheitsorientierte Orientierung für den nächsten empfohlenen Schritt.

Die Anwendung stellt keine Diagnose, nennt keine gesicherte Ursache und trifft keine Therapieentscheidung.

## Abgrenzung zur medizinischen Triage

Die Anwendung bildet kein professionelles Triage-System 1:1 ab. Gründe dafür sind:

- Es werden keine Vitalparameter wie Blutdruck, Puls, Sauerstoffsättigung oder Temperatur zuverlässig erfasst.
- Es findet keine körperliche Untersuchung statt.
- Die Angaben stammen ausschließlich aus der Nutzereingabe.
- Die Anwendung soll keine Behandlungspriorität innerhalb einer Notaufnahme festlegen.
- Die Stufen dienen ausschließlich der Orientierung für eine passende Handlungsempfehlung.

## Dringlichkeitsstufen

### Kritisch

Ein Fall gilt als kritisch, wenn die Nutzereingabe konkrete Hinweise auf eine mögliche akute Notfallsituation enthält. Dazu gehören Angaben, die mit den Red-Flag-Regeln der Anwendung übereinstimmen.

Diese Stufe bedeutet:

- Es liegen sicherheitsrelevante Warnzeichen vor.
- Die normale KI-Antwort wird nicht fortgeführt.
- Stattdessen wird eine feste Notfallmeldung ausgegeben.
- Die empfohlene Versorgungsebene ist Notruf 112 oder umgehende medizinische Hilfe.

Diese Stufe bedeutet nicht:

- Es wird keine Diagnose gestellt.
- Es wird nicht sicher behauptet, dass tatsächlich ein Notfall vorliegt.
- Es wird keine klinische Triage durchgeführt.
- Es wird nicht entschieden, welche konkrete Erkrankung vorliegt.

Bezug zu FA4 Red Flags:

Die Stufe „kritisch“ wird direkt durch erkannte Red Flags ausgelöst. Red Flags haben Vorrang vor allen anderen Stufen.

Bezug zu FA5 Versorgungsempfehlung:

Bei „kritisch“ wird keine normale Empfehlung wie Hausarztpraxis oder Selbstbeobachtung ausgegeben. Stattdessen erfolgt der Hinweis auf Notruf 112 oder sofortige medizinische Hilfe.

---

### Dringend

Ein Fall gilt als dringend, wenn keine kritische Red Flag erkannt wurde, die Angaben aber darauf hindeuten, dass eine zeitnahe ärztliche Abklärung sinnvoll ist.

Diese Stufe bedeutet:

- Die Situation wirkt anhand der Angaben nicht wie ein unmittelbarer Notfall.
- Es besteht aber ein erkennbarer Abklärungsbedarf.
- Die Beschwerden sollten nicht dauerhaft nur selbst beobachtet werden.
- Die Empfehlung verweist auf eine zeitnahe ärztliche Kontaktaufnahme.

Diese Stufe bedeutet nicht:

- Es wird keine Diagnose gestellt.
- Es wird kein automatischer Notruf empfohlen.
- Es wird nicht garantiert, dass die Situation ungefährlich ist.
- Es wird keine konkrete Behandlungsfrist im klinischen Sinne festgelegt.

Bezug zu FA4 Red Flags:

„Dringend“ wird nur verwendet, wenn keine blockierende Red Flag erkannt wurde. Sobald eine Red Flag erkannt wird, wird die Stufe „kritisch“ verwendet.

Bezug zu FA5 Versorgungsempfehlung:

Bei „dringend“ wird eine zeitnahe ärztliche Abklärung empfohlen, zum Beispiel über Hausarztpraxis, ärztlichen Bereitschaftsdienst 116117 oder eine passende Facharztpraxis.

---

### Nicht dringend

Ein Fall gilt als nicht dringend, wenn keine Red Flag erkannt wurde und die Angaben eher auf ein leichtes, stabiles oder nicht akut wirkendes Anliegen hinweisen.

Diese Stufe bedeutet:

- Es gibt anhand der Angaben keinen Hinweis auf eine akute Notfallsituation.
- Eine sofortige medizinische Abklärung wird nicht vorrangig empfohlen.
- Selbstbeobachtung, allgemeine Gesundheitsinformationen oder ein regulärer Arzttermin können als nächste Schritte genannt werden.
- Die Empfehlung enthält Hinweise, wann erneut medizinische Hilfe gesucht werden sollte.

Diese Stufe bedeutet nicht:

- Die Beschwerden sind nicht automatisch harmlos.
- Die Anwendung schließt keine Erkrankung aus.
- Die Anwendung garantiert nicht, dass keine Gefahr besteht.
- Die Anwendung ersetzt keine ärztliche Untersuchung.

Bezug zu FA4 Red Flags:

„Nicht dringend“ darf nur verwendet werden, wenn keine Red Flag erkannt wurde.

Bezug zu FA5 Versorgungsempfehlung:

Bei „nicht dringend“ kann die Empfehlung auf Selbstbeobachtung, Gesundheitsinformationen, präventive Angebote oder einen regulären Arzttermin verweisen.

---

### Nicht eindeutig

Ein Fall gilt als nicht eindeutig, wenn die vorhandenen Angaben nicht ausreichen, um eine sichere Orientierung für den nächsten Schritt abzuleiten.

Diese Stufe bedeutet:

- Die Nutzereingabe ist zu unvollständig, zu allgemein oder widersprüchlich.
- Es fehlen relevante Informationen zur Einordnung.
- Das System soll eine gezielte Rückfrage stellen oder vorsichtig zu ärztlicher Abklärung raten.
- Die Stufe verhindert, dass unklare Fälle fälschlich als nicht dringend eingestuft werden.

Diese Stufe bedeutet nicht:

- Die Situation ist nicht automatisch ungefährlich.
- Es wird keine Entwarnung gegeben.
- Es wird keine Diagnose gestellt.
- Es wird keine endgültige Versorgungsebene festgelegt, solange entscheidende Informationen fehlen.

Bezug zu FA4 Red Flags:

Wenn trotz unklarer Angaben eine Red Flag erkannt wird, hat „kritisch“ Vorrang. Wenn keine Red Flag erkannt wird, aber Informationen fehlen, kann „nicht eindeutig“ verwendet werden.

Bezug zu FA5 Versorgungsempfehlung:

Bei „nicht eindeutig“ soll die Anwendung bevorzugt eine kurze Rückfrage stellen. Falls keine Klärung möglich ist, soll eine vorsichtige Handlungsempfehlung gegeben werden.

## Entscheidungsreihenfolge

Die Dringlichkeitsstufen werden in folgender Reihenfolge geprüft:

1. Prüfung auf Red Flags nach FA4  
   Wenn eine Red Flag erkannt wird, wird die Stufe „kritisch“ verwendet.

2. Prüfung auf ausreichende Angaben  
   Wenn entscheidende Informationen fehlen, wird die Stufe „nicht eindeutig“ verwendet.

3. Prüfung auf zeitnahen ärztlichen Abklärungsbedarf  
   Wenn kein Notfall vorliegt, aber eine ärztliche Abklärung sinnvoll erscheint, wird die Stufe „dringend“ verwendet.

4. Prüfung auf niedrig belastende, stabile Anliegen  
   Wenn keine Red Flag, keine deutliche Verschlechterung und kein klarer zeitnaher Abklärungsbedarf vorliegen, wird die Stufe „nicht dringend“ verwendet.

## Sicherheitsregel

Keine Red Flag bedeutet nicht automatisch „nicht dringend“.

Wenn die Angaben unvollständig, widersprüchlich oder nicht ausreichend bewertbar sind, wird die Stufe „nicht eindeutig“ verwendet.