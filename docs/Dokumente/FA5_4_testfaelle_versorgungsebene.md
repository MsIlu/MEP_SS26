# FA5.4 – Testfälle für Versorgungsebene und Handlungsempfehlung

---

## Hinweis

Die Testfälle in diesem Dokument sind derzeit ausschließlich definiert und beschreiben die geplante Testbasis (Testdesign).

Die tatsächliche Testausführung sowie die dazugehörigen Testergebnisse werden im Verlauf der Implementierung nachgetragen.

---

## FA5.4.1: Testfälle für unterschiedliche Dringlichkeitsstufen erstellen

| Testfall-ID | Eingabe | Erwartete Dringlichkeitsstufe |
|------------|----------|-------------------------------|
| TF-DR-01 | Ich habe plötzlich sehr starke Brustschmerzen und bekomme kaum Luft | Notfall |
| TF-DR-02 | Ich kann plötzlich nicht mehr richtig sprechen und eine Gesichtshälfte hängt runter | Notfall |
| TF-DR-03 | Mein 2-jähriges Kind hat seit 2 Tagen 40°C Fieber und wirkt sehr schlapp | Notfall |
| TF-DR-04 | Jemand ist nach einem Sturz bewusstlos geworden und reagiert nicht | Notfall |
| TF-DR-05 | Ich habe hohes Fieber und starke Kopfschmerzen mit steifem Nacken | Notfall |
| TF-DR-06 | Nach einem Insektenstich schwillt mein Hals zu und ich bekomme schlechter Luft | Notfall |
| TF-DR-07 | Ich sehe auf einem Auge plötzlich gar nichts mehr | Notfall |
| TF-DR-08 | Ich habe seit 2 Tagen starke Ohrenschmerzen | Arzt |
| TF-DR-09 | Ich habe seit einiger Zeit Rückenschmerzen, vor allem beim Bewegen | Arzt |
| TF-DR-10 | Ich habe plötzlich Herzrasen und mir ist schwindelig | Arzt |
| TF-DR-11 | Ich habe mir den Fuß umgeknickt und er ist geschwollen und schmerzhaft | Arzt |
| TF-DR-12 | Ich habe einen juckenden Hautausschlag am Arm seit ein paar Tagen | Arzt |
| TF-DR-13 | Ich muss sehr oft Wasserlassen und es brennt dabei | Arzt |
| TF-DR-14 | Mein Auge ist rot und verklebt und es kommt etwas gelblicher Ausfluss | Arzt |
| TF-DR-15 | Ich habe seit 2 Tagen leichten Husten und Schnupfen | Selbstbeobachtung |
| TF-DR-16 | Ich habe leichte Kopfschmerzen seit gestern | Selbstbeobachtung |
| TF-DR-17 | Ich habe Muskelkater nach körperlicher Arbeit | Selbstbeobachtung |
| TF-DR-18 | Mir ist leicht übel nach sehr fettigem Essen | Selbstbeobachtung |

---

## FA5.4.2: Testfälle für unterschiedliche Versorgungsebenen erstellen

| Testfall-ID | Eingabe | Erwartete Versorgungsebene |
|------------|----------|----------------------------|
| TF-VE-01 | Ich bin mit dem Fahrrad gestürzt und habe eine offene, stark blutende Beinverletzung | Notfall |
| TF-VE-02 | Ich habe mich tief geschnitten und die Blutung hört nicht auf | Notfall |
| TF-VE-03 | Ich habe starke Atemnot und bekomme kaum Luft (Asthma-Anfall) | Notfall |
| TF-VE-04 | Ich habe einen Krampfanfall gehabt und war kurz bewusstlos | Notfall |
| TF-VE-05 | Ich habe mich stark verbrannt und es bilden sich Blasen | Notfall |
| TF-VE-06 | Nach einem Medikament bekomme ich plötzlich eine starke allergische Reaktion mit Schwellung im Gesicht | Notfall |
| TF-VE-07 | Ich habe mehrmals Blut erbrochen | Notfall |
| TF-VE-08 | Ich habe Fieber und Schmerzen beim Wasserlassen | Arzt |
| TF-VE-09 | Mein Knie ist nach Sport stark geschwollen und schmerzt | Arzt |
| TF-VE-10 | Ein Insektenstich ist stark rot geworden und wird immer größer | Arzt |
| TF-VE-11 | Ich habe starke Zahnschmerzen und meine Wange ist geschwollen | Arzt |
| TF-VE-12 | Ich habe seit mehreren Tagen Durchfall | Arzt |
| TF-VE-13 | Ich habe Rückenschmerzen, die ins Bein ausstrahlen | Arzt |
| TF-VE-14 | Ich habe immer wieder Migräne mit Lichtempfindlichkeit | Arzt |
| TF-VE-15 | Ich habe leichten Sonnenbrand ohne Blasen | Selbstbeobachtung |
| TF-VE-16 | Meine Haut ist im Winter sehr trocken | Selbstbeobachtung |

---

## FA5.4.3: Testen, ob Red-Flag-Fälle korrekt zu einer Notfallmaßnahme führen

| Testfall-ID | Eingabe | Erwartetes Ergebnis |
|------------|----------|---------------------|
| TF-RF-01 | Ich habe plötzlich die schlimmsten Kopfschmerzen meines Lebens bekommen | Notfall |
| TF-RF-02 | Ich habe starke Brustschmerzen und es zieht in den linken Arm | Notfall |
| TF-RF-03 | Ich erbreche Blut | Notfall |
| TF-RF-04 | Ich kann meine Beine plötzlich nicht mehr bewegen | Notfall |
| TF-RF-05 | Ich habe mich schwer verbrannt (große Brandwunde) | Notfall |
| TF-RF-06 | Ich habe plötzlich starke Atemprobleme nach Rauch | Notfall |
| TF-RF-07 | Ich habe starken Durchfall mit Blut und fühle mich sehr schwach | Notfall |
| TF-RF-08 | Ich bin kurz ohnmächtig geworden und fühle mich immer noch schlecht | Notfall |
| TF-RF-09 | Mein Baby (unter 1 Jahr) hat 40°C Fieber und trinkt kaum | Notfall |
| TF-RF-10 | Ich habe plötzlich sehr starke Bauchschmerzen | Notfall |
| TF-RF-11 | Ich bin Diabetiker und habe starke Unterzuckerung mit Verwirrtheit | Notfall |
| TF-RF-12 | Ich wurde von einem Hund gebissen und die Wunde blutet stark | Notfall |
| TF-RF-13 | Ich habe etwas ins Auge bekommen und sehe plötzlich schlechter | Notfall |
| TF-RF-14 | Ich habe vermutlich eine gefährliche Substanz verschluckt | Notfall |

---

## FA5.4.4: Testen, ob nicht dringende Fälle keine unnötige Notfallempfehlung erhalten

| Testfall-ID | Eingabe | Erwartetes Ergebnis |
|------------|----------|---------------------|
| TF-NF-01 | Ich habe leichte Halsschmerzen seit gestern | Selbstbeobachtung |
| TF-NF-02 | Ich habe Muskelkater nach dem Sport | Selbstbeobachtung |
| TF-NF-03 | Ich habe leichte Kopfschmerzen ohne weitere Beschwerden | Selbstbeobachtung |
| TF-NF-04 | Ich habe einen normalen Schnupfen | Selbstbeobachtung |
| TF-NF-05 | Ich habe mich leicht geschnitten, die Wunde ist schon zu | Selbstbeobachtung |
| TF-NF-06 | Ich habe leichtes Sodbrennen nach dem Essen | Selbstbeobachtung |
| TF-NF-07 | Ich habe Rückenschmerzen nach langem Sitzen | Selbstbeobachtung |
| TF-NF-08 | Ich bin leicht heiser nach viel Sprechen | Selbstbeobachtung |
| TF-NF-09 | Ich habe trockenen Husten bei kalter Luft | Selbstbeobachtung |
| TF-NF-10 | Ich habe mich leicht gestoßen, es tut nur ein bisschen weh | Selbstbeobachtung |
| TF-NF-11 | Ich bin einfach nur müde nach wenig Schlaf | Selbstbeobachtung |
| TF-NF-12 | Mir ist kurz schlecht im Auto geworden | Selbstbeobachtung |
| TF-NF-13 | Meine Lippen sind trocken wegen der Kälte | Selbstbeobachtung |
| TF-NF-14 | Ich bin etwas gestresst und unkonzentriert | Selbstbeobachtung |

---

**Gesamt**: **62 Testfälle** 
