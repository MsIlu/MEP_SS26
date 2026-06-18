# FA5.4 – Testfälle für Versorgungsebene und Handlungsempfehlung

---

## Hinweis

Die Testfälle in diesem Dokument sind derzeit ausschließlich definiert und beschreiben die geplante Testbasis (Testdesign).

Die tatsächliche Testausführung sowie die dazugehörigen Testergebnisse werden im Verlauf der Implementierung nachgetragen.

---

## FA5.4.1 – Testfälle für unterschiedliche Dringlichkeitsstufen

| Testfall-ID | Eingabe | Erwartete Dringlichkeitsstufe |
|------------|--------|-------------------------------|
| TF-DR-01 | Starke Brustschmerzen, Atemnot | Notfall |
| TF-DR-02 | Sprachstörung, einseitige Lähmung (plötzlich) | Notfall |
| TF-DR-03 | Kind 2 Jahre, 40°C Fieber seit 2 Tagen | Notfall |
| TF-DR-04 | Starke Ohrenschmerzen seit 2 Tagen | Arzt |
| TF-DR-05 | Mittlere Rückenschmerzen nach Belastung | Arzt |
| TF-DR-06 | Mittlerer Husten, Schnupfen seit 2 Tagen | Selbstbeobachtung |
| TF-DR-07 | Seit 1 Tag leichte Kopfschmerzen | Selbstbeobachtung |

---

## FA5.4.2 – Testfälle für unterschiedliche Versorgungsebenen

| Testfall-ID | Eingabe | Erwartete Versorgungsebene |
|------------|--------|----------------------------|
| TF-VE-01 | Schwellung im Halsbereich nach Insektenstich, Atembeschwerden | Notfall |
| TF-VE-02 | Tiefe Wunde am Unterarm, starke Blutung | Notfall |
| TF-VE-03 | Brennen beim Wasserlassen, häufiger Harndrang seit 2 Tagen | Arzt |
| TF-VE-04 | Gerötetes Auge, Juckreiz, Sekretbildung seit 2 Tagen | Arzt |
| TF-VE-05 | Durchfall und Übelkeit seit 24 Stunden, ausreichende Flüssigkeitsaufnahme möglich | Selbstbeobachtung |
| TF-VE-06 | Muskelschmerzen in den Oberschenkeln nach intensivem Training nach 1 Tag | Selbstbeobachtung |
| TF-VE-07 | Haut gerötet, keine Blasenbildung, Allgemeinzustand gut, seit 8 Stunden | Selbstbeobachtung |

---

## FA5.4.3 – Red-Flag-Fälle (Notfall muss ausgelöst werden)

| Testfall-ID | Eingabe | Erwartetes Ergebnis |
|------------|--------|---------------------|
| TF-RF-01 | Krampfanfall seit 2 Minuten | Notfall |
| TF-RF-02 | „Stärkste Kopfschmerzen meines Lebens“, plötzlich begonnen vor 15 Minuten | Notfall |
| TF-RF-03 | Sturz mit starken Brustschmerzen und Atemproblemen seit 10 Minuten | Notfall |
| TF-RF-04 | Schwere Verbrennung an Arm und Brust, Ereignis vor 20 Minuten | Notfall |
| TF-RF-05 | Mehrfaches Erbrechen mit sichtbarem Blut seit 1 Stunde | Notfall |
| TF-RF-06 | Plötzlicher Sehverlust auf einem Auge seit 30 Minuten | Notfall |
| TF-RF-07 | Starke allergische Reaktion mit Schwellung im Gesicht und Atemnot nach Nahrungsaufnahme, Symptome seit 10 Minuten | Notfall |

---

## FA5.4.4 – Keine unnötigen Notfallempfehlungen (False-Positive-Tests)

| Testfall-ID | Eingabe | Erwartetes Ergebnis |
|------------|--------|---------------------|
| TF-NF-01 | Leichte Halsschmerzen seit 1 Tag, kein Fieber, Allgemeinzustand gut | Selbstbeobachtung |
| TF-NF-02 | Leichtes Ziehen im Knie nach Sport, normal belastbar | Selbstbeobachtung |
| TF-NF-03 | Juckende Hautstelle nach Mückenstich, keine Ausbreitung | Selbstbeobachtung |
| TF-NF-04 | Leichter Schnupfen mit gelegentlichem Niesen, kein Krankheitsgefühl | Selbstbeobachtung |
| TF-NF-05 | Leichte Kopfschmerzen nach wenig Schlaf, keine weiteren Symptome | Selbstbeobachtung |
| TF-NF-06 | Kleine oberflächliche Schürfwunde, keine Blutung mehr, sauber versorgt | Selbstbeobachtung |
| TF-NF-07 | Gelegentliches Sodbrennen (Rückfluss von Magensäure in die Speiseröhre) nach fettigem Essen, keine starken Schmerzen | Selbstbeobachtung |