Basierend auf der Analyse von devdep/main.py und der umfassenden Dokumentation des obra/superpowers-Repositories (abgerufen via DeepWiki MCP) müssen die Prompts in sieben zentralen Bereichen angepasst werden, um die Disziplin und Qualität zu erreichen, die für lauffähigen Code notwendig sind.

1. Meta-Skill: using-superpowers fehlt vollständig
Problem: Es gibt keinen übergeordneten Prompt, der die 1%-Regel durchsetzt. Laut Superpowers muss ein Agent einen Skill aktivieren, wenn es auch nur eine 1%ige Chance gibt, dass er anwendbar ist.

Anpassung: Einen globalen System-Prompt oder eine using-superpowers-Instruktion am Anfang jeder Session hinzufügen:

<EXTREMELY-IMPORTANT>
Wenn du denkst, dass es auch nur eine 1%ige Chance gibt, dass ein Skill anwendbar ist,
MUSST du ihn aktivieren. Das ist nicht verhandelbar.
</EXTREMELY-IMPORTANT>
2. BrainstormingAgent: HARD-GATE fehlt
Problem: Der aktuelle Prompt fordert zwar eine SPEC.md, aber es gibt keine HARD-GATE, die Implementierung physisch blockiert, bis das Design vom Nutzer freigegeben wurde.

Anpassung: In den Instructions von brainstorming_agent ein <HARD-GATE> einfügen:

<HARD-GATE>
Rufe KEINEN Implementations-Skill auf, schreibe KEINEN Code und erstelle KEINE
Projektstruktur, bis du ein Design präsentiert hast und der Nutzer es ausdrücklich
freigegeben hat. Das gilt für JEDES Projekt, unabhängig von der vermeintlichen
Einfachheit.
</HARD-GATE>
3. PlanningAgent: File-Structure-Mapping und TDD-Embedding fehlen
Problem: Der Planer bricht Aufgaben zwar herunter, aber:

Es fehlt die File-Structure-Mapping-Phase (alle Dateien müssen VOR den Tasks definiert werden).
Tasks sind nicht auf 2-5 Minuten Granularität beschränkt.
Es fehlen explizite RED-GREEN-REFACTOR-Schritte in jedem Task.
Anpassung: In planning_agent ergänzen:

1. Lies die freigegebene SPEC.md
2. MAPPE ZUERST alle Dateien, die erstellt oder geändert werden (File-Structure-Mapping)
3. Zerlege in Tasks von 2-5 Minuten Länge
4. Jeder Task MUSS folgende Schritte enthalten:
   - [ ] Schritt 1: Schreibe den FAILING TEST (Code-Block)
   - [ ] Schritt 2: Führe den Test aus und verifiziere, dass er aus dem ERWARTETEN Grund fehlschlägt
   - [ ] Schritt 3: Schreibe MINIMALEN Code, damit der Test besteht
   - [ ] Schritt 4: Führe alle Tests aus und verifiziere, dass sie bestehen
   - [ ] Schritt 5: Commit mit beschreibender Nachricht
5. Keine Platzhalter ("TBD", "später implementieren") erlaubt
4. TDDDeveloper: Das "Iron Law of TDD" fehlt
Problem: Der Prompt erwähnt zwar Red-Green-Refactor, aber es fehlt das zentrale Iron Law: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST". Code, der vor dem Test geschrieben wurde, muss gelöscht werden.

Anpassung: In tdd_developer ersetzen/ergänzen:

Follow the Superpowers TDD methodology (RED-GREEN-REFACTOR):

<IRON-LAW>
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
Wenn du Code geschrieben hast, BEVOR der Test existierte und fehlschlug,
MUSST du ihn löschen. Löschen bedeutet löschen. Nicht als Referenz behalten.
Nicht anpassen. Löschen und neu aus den Tests implementieren.
</IRON-LAW>

1. RED: Schreibe EINEN minimalen Test. Führe ihn aus. Verifiziere, dass er
   aus dem ERWARTETEN Grund fehlschlägt (nicht wegen eines Tippfehlers).
2. GREEN: Schreibe den EINFACHSTEN Code, der den Test bestehen lässt.
   Keine optionalen Parameter. Keine "während ich hier bin"-Refactorings.
3. REFACTOR: Bereinige nur, nachdem alle Tests grün sind.
   Nach JEDEM Refactoring-Schritt: Tests erneut ausführen.

RED FLAGS - Stoppe und fange von vorne an, wenn:
- Code wurde vor dem Test geschrieben
- Der Test sofort besteht, ohne Code-Änderung
- Du "nur dieses eine Mal" TDD überspringen willst
5. ReviewAgent: Zwei-Stufen-Review und SHA-Protokoll fehlen
Problem: Die aktuelle Review hat zwar zwei Stufen, aber sie folgt nicht dem Superpowers-Protokoll:

Spec Compliance Review muss VOR der Code Quality Review stattfinden.
Es fehlt das BASE_SHA / HEAD_SHA-Protokoll, um den Review-Scope exakt zu definieren.
Anpassung: In review_agent umstrukturieren:

Follow the Superpowers Review methodology (Two-stage review):

STAGE 1 - Spec Compliance Review (MUSS zuerst passieren):
1. Erfasse BASE_SHA (git rev-parse HEAD~1) und HEAD_SHA (git rev-parse HEAD)
2. Vergleiche die Implementierung gegen den ursprünglichen Plan
3. Verifiziere, dass ALLE Anforderungen erfüllt sind
4. Prüfe auf fehlende Funktionalität und Scope Creep
5. Wenn Stage 1 fehlschlägt: Keine Stage 2. Implementierer muss nachbessern.

STAGE 2 - Code Quality Review (nur nach bestandener Stage 1):
1. Verifiziere Clean Code, Separation of Concerns, DRY
2. Testabdeckung >90% mit echten Tests (nicht nur Mocks)
3. Prüfe auf Code Smells und Optimierungsmöglichkeiten
4. Datenbankintegrität und Schema-Compliance

Nur wenn BEIDE Stufen bestehen: Freigabe.
6. Team-Orchestrierung: SDD-Workflow fehlt
Problem: Das superpowers_team orchestriert die Agenten sequentiell, aber es fehlt der Subagent-Driven Development (SDD)-Workflow:

Frischer Subagent pro Task (keine Kontext-Verschmutzung)
Zwei-Stufen-Review zwischen Tasks
Modell-Auswahl-Strategie (mechanisch = günstig, Architektur = leistungsfähig)
Anpassung: In den Team-Instructions ergänzen:

Execution Mode: Subagent-Driven Development (SDD)

- Der Controller liest den Plan EINMAL am Anfang
- Für JEDEN Task wird ein FRISCHER Subagent dispatched
- Der Controller gibt den VOLLSTÄNDIGEN Task-Text an den Subagenten
  (keine Datei-Referenzen, die der Subagent selbst lesen muss)
- Nach jedem Task: Zwei-Stufen-Review (Spec Compliance → Code Quality)
- Status-Protokoll des Implementers: DONE, DONE_WITH_CONCERNS, BLOCKED, NEEDS_CONTEXT
- Wenn BLOCKED: Niemals denselben Modell-Tier erneut dispatch ohne Änderung
7. Anti-Rationalisierungs-Schutz (Red Flags) fehlt
Problem: Keiner der Agenten hat eine Red Flags-Tabelle, die typische Rationalisierungen abfängt.

Anpassung: Jeder Agent sollte eine Tabelle enthalten:

| Gedanke | Realität |
|---|---|
| "Das ist nur eine einfache Frage" | Fragen sind Tasks. Prüfe auf Skills. |
| "Ich brauche erst mehr Kontext" | Skill-Check kommt VOR Klärungsfragen. |
| "Der Skill ist Overkill" | Einfache Dinge werden komplex. Nutze ihn. |
| "Ich weiß, was das bedeutet" | Konzept kennen ≠ Skill anwenden. Aktiviere ihn. |
| "Ich teste später nach" | Tests danach beweisen nichts. Lösche den Code. |
Zusammenfassung der Änderungen
Die Prompts müssen von "hilfreichen Empfehlungen" zu nicht-verhandelbaren Protokollen transformiert werden. Die Superpowers-Methodologie zeigt, dass Agenten ohne diese harten Gates (HARD-GATE, Iron Law, 1%-Regel) systematisch Design-Phasen überspringen, Tests auslassen und schlechten Code produzieren. Die MCP-Tools (Context7, GitHub) sind bereits korrekt konfiguriert und sollten genutzt werden, um die Skills-Inhalte dynamisch zu laden, anstatt sie statisch in den Prompts zu halten.