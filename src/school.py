# -*- coding: utf-8 -*-
"""Cours en écoles et universités (FR/EN).
Module titles come from academic Bac+5 programmes in infrastructure, governance and security.
Duration, content and assessment are set by each institution's pedagogical team: never publish
durations here. Do not name a school or a certification code publicly without Mohamed's approval.
Hands-on offensive security, SOC/forensics and SIEM are deliberately not offered.
The worked example (ex_*) follows the same rules: sequences, not days or hours, and no block or
competency codes. Teaching facts (teach) come from the reference letters in the private repo."""

FR = dict(
    page_h1="Formations et cours",
    page_intro=("Deux façons de travailler ensemble : des formations construites pour vos équipes, "
                "ou des cours intégrés aux programmes des écoles et des universités."),
    doors=[
        ("#entreprise", "Formations en entreprise",
         "9 formations 2026 en intra-entreprise : IA agentique, AI Act, DORA, NIS2, FinOps, SRE, SLA/OLA/UC. "
         "Programme, durée et livrables définis par Metafive.ai."),
        ("#cours", "Cours en écoles et universités",
         "Des modules de Bachelor, Mastère et Master en gouvernance, infrastructures, projets et sécurité. "
         "Durée et contenu fixés par les responsables pédagogiques."),
    ],
    ent_h2="Formations en entreprise",
    h2="Cours en écoles et universités",
    intro=("Pour les écoles d'ingénieurs, les écoles du numérique, les universités et la formation continue. "
           "J'interviens sur les modules ci-dessous en apportant des cas réels tirés de 30 ans de pilotage "
           "d'infrastructures et de services, en Europe et au Moyen-Orient."),
    how_h3="Fonctionnement",
    how=[
        ("Votre programme", "La durée, le contenu, les objectifs et les modalités d'évaluation sont fixés par "
                            "l'établissement et le référentiel de la certification."),
        ("Niveaux", "Bachelor, Mastère, MSc, Master universitaire, formation continue et executive education, "
                    "de Bac+3 à Bac+5."),
        ("Formats", "Cours, TD, études de cas réels, projets tutorés, participation aux jurys. "
                    "Compatible avec les rythmes d'alternance."),
        ("Langues", "En français ou en anglais ; arabe possible. Sur site en Île-de-France ou à distance."),
    ],
    groups_h3="Modules",
    groups=[
        ("Gouvernance et gestion des services",
         "ITIL v2, v3 et 4, ISO/IEC 20000, chaîne SLA, OLA, UC.",
         ["Gouvernance des infrastructures (ITIL)",
          "Fourniture des services : catalogue, SLA, OLA, UC",
          "IT Service Management (ITSM)",
          "Gestion du support",
          "Mise en production et amélioration continue",
          "IT Asset Management (ITAM)",
          "Numérique responsable : FinOps et sobriété"]),
        ("Conception et pilotage des infrastructures",
         "Cloud, hybride et plateformes à grande échelle.",
         ["Conception d'infrastructures cloud et hybrides",
          "Automatisation et usine logicielle (CI/CD, Platform Engineering)",
          "Gestion des identités et des accès (IAM)"]),
        ("Pilotage de projets et conduite du changement",
         "Programmes de transformation, équipes multiculturelles, budgets.",
         ["Étude d'avant-projet",
          "Cahier des charges et appels d'offres",
          "Management de projet",
          "Management des équipes",
          "Gestion des coûts",
          "Gestion de la recette",
          "Contrats de prestation : engagements de service et pénalités",
          "Communication professionnelle"]),
        ("Sécurité, conformité et audit",
         "ISO 27001, ISO 22301, DORA, NIS2, AI Act : le volet gouvernance.",
         ["Audit des infrastructures et conformité",
          "Politique de sécurité",
          "Management de la sécurité et continuité d'activité",
          "Architecture d'infrastructure sécurisée",
          "Audit de sécurité organisationnel",
          "Veille réglementaire et cyber multilingue"]),
        ("Projets tutorés et jurys",
         "Encadrement de bout en bout, sur des sujets proches du terrain.",
         ["Projets : gestion des services, conception et pilotage d'infrastructure",
          "Projets : management de projet, management du support",
          "Projets : audit d'infrastructures, volet conformité",
          "Jurys d'épreuves certifiantes et de projets professionnels"]),
    ],
    ex_h3="Exemple d'intervention : gestion des identités et des accès (IAM)",
    ex_intro=("Un module tel que je le construis à partir de la fiche de l'établissement : compétences visées, "
              "objectifs pédagogiques, plan, exercices et livrables. Chaque séquence alterne apports, cas réels "
              "et atelier avec livrable."),
    ex_parts=[
        ("Fondements et modèles",
         "Enjeux, acteurs et risques ; modèles centralisé, décentralisé et fédéré.",
         ["Atelier : audit de risques d'un système existant",
          "Atelier : choix argumenté d'un modèle pour une organisation"]),
        ("Processus et technologies",
         "Provisioning, déprovisioning, gestion et revue des accès ; annuaires, fédération et SSO, MFA.",
         ["Atelier : plan des processus de gestion des identités",
          "Atelier : choix des briques et plan de mise en œuvre"]),
        ("Conformité et audit",
         "RGPD, ISO 27001, NIST SP 800-63 ; suivi, audit et actions correctives.",
         ["Atelier : plan d'audit de conformité",
          "Restitution croisée et évaluation"]),
    ],
    ex_cases_h4="Cas réels apportés",
    ex_cases=["Programme Portail e-Government et Single Sign-On d'Abu Dhabi",
              "Comptes, rôles et journalisation d'un environnement AWS multi-comptes",
              "Le contrôle d'accès vu par l'auditeur ISO 27001"],
    ex_method_h4="Pédagogie",
    ex_method=("Cours interactifs appuyés sur des cas réels, ateliers guidés avec livrables, classe inversée, "
               "évaluation formative (QCM, audits croisés, revue par les pairs), projet fil rouge."),
    teach_h3="Expérience d'enseignement",
    teach=["Enseignement dès 1998 : applications informatiques et programmes de formation à l'Institut de "
           "Développement Administratif de Doha.",
           "Formateur aux 15ᵉ Jeux asiatiques de Doha (2006) : sessions d'accueil et de formation générale, "
           "programme de leadership ; plus de 31 500 personnes formées par le programme.",
           "Création de la première académie e-Learning Microsoft du Golfe : plus de 1 000 professionnels IT formés.",
           "Série vidéo « From SLI to SLO », ateliers et communauté « SRE Champions » au sein d'un grand groupe "
           "bancaire français."],
    cta_h3="Responsable pédagogique ?",
    cta_p="Envoyez-moi la fiche du module : je vous réponds avec une proposition d'intervention alignée sur votre référentiel.",
    cta_mail="Écrire à",
    note=("Les tests d'intrusion, le SOC, l'analyse forensique et l'exploitation d'outils SIEM ne font pas partie "
          "de mes interventions : je peux les co-animer avec un expert technique."),
    home_h3="Cours en écoles et universités",
    home_p=("Bachelor, Mastère et Master : gouvernance ITIL, gestion des services, conception d'infrastructures, "
            "pilotage de projets, sécurité et conformité. Durée et contenu fixés par vos responsables pédagogiques."),
    home_cta="Voir les modules",
)

EN = dict(
    page_h1="Training and courses",
    page_intro=("Two ways to work together: training built for your teams, or courses that are part of "
                "school and university programmes."),
    doors=[
        ("#entreprise", "In-house training",
         "9 in-house courses for 2026: agentic AI, the AI Act, DORA, NIS2, FinOps, SRE, SLA/OLA/UC. "
         "Programme, duration and deliverables defined by Metafive.ai."),
        ("#cours", "Courses for schools and universities",
         "Bachelor's and Master's modules in governance, infrastructure, projects and security. "
         "Duration and content set by the programme leads."),
    ],
    ent_h2="In-house training",
    h2="Courses for schools and universities",
    intro=("For engineering schools, digital schools, universities and continuing education. "
           "I teach the modules below with real cases drawn from 30 years of running infrastructure and services "
           "in Europe and the Middle East."),
    how_h3="How it works",
    how=[
        ("Your programme", "Duration, content, objectives and assessment are set by the institution and the "
                           "certification framework."),
        ("Levels", "Bachelor's, Master's, MSc, university Master's, continuing and executive education."),
        ("Formats", "Lectures, tutorials, real case studies, supervised projects, exam panels. "
                    "Compatible with work-study schedules."),
        ("Languages", "In French or English; Arabic possible. On site in the Paris region or remote."),
    ],
    groups_h3="Modules",
    groups=[
        ("Governance and service management",
         "ITIL v2, v3 and 4, ISO/IEC 20000, the SLA, OLA, UC chain.",
         ["Infrastructure governance (ITIL)",
          "Service delivery: catalogue, SLA, OLA, UC",
          "IT Service Management (ITSM)",
          "Support management",
          "Release management and continuous improvement",
          "IT Asset Management (ITAM)",
          "Sustainable IT: FinOps and efficiency"]),
        ("Infrastructure design and management",
         "Cloud, hybrid and platforms at scale.",
         ["Cloud and hybrid infrastructure design",
          "Automation and software factory (CI/CD, Platform Engineering)",
          "Identity and access management (IAM)"]),
        ("Project management and change",
         "Transformation programmes, multicultural teams, budgets.",
         ["Pre-project study",
          "Requirements and tenders",
          "Project management",
          "People management",
          "Cost management",
          "Acceptance testing management",
          "Service contracts: service commitments and penalties",
          "Professional communication"]),
        ("Security, compliance and audit",
         "ISO 27001, ISO 22301, DORA, NIS2, AI Act: the governance side.",
         ["Infrastructure audit and compliance",
          "Security policy",
          "Security management and business continuity",
          "Secure infrastructure architecture",
          "Organisational security audit",
          "Multilingual regulatory and cyber watch"]),
        ("Supervised projects and panels",
         "End-to-end supervision, on topics close to real operations.",
         ["Projects: service management, infrastructure design and management",
          "Projects: project management, support management",
          "Projects: infrastructure audit, compliance side",
          "Certification exam and professional project panels"]),
    ],
    ex_h3="A worked example: identity and access management (IAM)",
    ex_intro=("A module as I build it from the institution's module description: target competencies, learning "
              "objectives, outline, exercises and deliverables. Each sequence combines input, real cases and a "
              "workshop with a deliverable."),
    ex_parts=[
        ("Foundations and models",
         "Stakes, actors and risks; centralised, decentralised and federated models.",
         ["Workshop: risk audit of an existing system",
          "Workshop: reasoned choice of a model for an organisation"]),
        ("Processes and technologies",
         "Provisioning, deprovisioning, access management and access reviews; directories, federation and SSO, MFA.",
         ["Workshop: plan for the identity management processes",
          "Workshop: choice of building blocks and implementation plan"]),
        ("Compliance and audit",
         "GDPR, ISO 27001, NIST SP 800-63; monitoring, audit and corrective actions.",
         ["Workshop: compliance audit plan",
          "Peer presentations and assessment"]),
    ],
    ex_cases_h4="Real cases I bring",
    ex_cases=["The Abu Dhabi e-Government Portal and Single Sign-On programme",
              "Accounts, roles and logging in a multi-account AWS environment",
              "Access control as seen by the ISO 27001 auditor"],
    ex_method_h4="Teaching methods",
    ex_method=("Interactive lectures built on real cases, guided workshops with deliverables, flipped classroom, "
               "formative assessment (quizzes, cross-audits, peer review), a project running through the year."),
    teach_h3="Teaching experience",
    teach=["Teaching since 1998: computer applications and training programmes at the Institute of "
           "Administrative Development in Doha.",
           "Trainer at the 15th Asian Games in Doha (2006): induction and general training sessions, leadership "
           "programme; more than 31,500 people trained by the programme.",
           "Founded the first Microsoft e-Learning academy in the Gulf: more than 1,000 IT professionals trained.",
           "“From SLI to SLO” video series, workshops and an “SRE Champions” community inside a major French "
           "banking group."],
    cta_h3="Programme lead?",
    cta_p="Send me the module description: I will reply with a teaching proposal aligned with your framework.",
    cta_mail="Write to",
    note=("Penetration testing, SOC work, forensics and hands-on SIEM tooling are not part of what I teach: "
          "I can co-teach them with a technical expert."),
    home_h3="Courses for schools and universities",
    home_p=("Bachelor's and Master's modules: ITIL governance, service management, infrastructure design, "
            "project management, security and compliance. Duration and content set by your programme leads."),
    home_cta="See the modules",
)
