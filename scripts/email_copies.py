"""Copies reais de emails conversacionais, usadas como exemplo de aplicação em todos os
design systems de email (build-email-ds*.py).

Os emails da Asimov quase nunca têm título: abrem direto na conversa. Cada copy é uma
lista de blocos:

    ("p", texto)            parágrafo
    ("cta", rótulo)         botão (no original, a linha com 👉 [RÓTULO])
    ("ul", [itens])         lista
    ("sign", nome, cargo)   assinatura (cargo pode ser "")
    ("ps", texto)           pós-escrito

"tom" escolhe o peso do botão nos sistemas que têm dois níveis (hoje, o da Black):
"chamativo" quando a ação é o objetivo do email (cadastro, compra), "discreto" quando o
botão é um convite (relacionamento, conteúdo). O mesmo email não mistura os dois.
"""

COPIES = [
    {
        "id": "em-001",
        "code": "EM-001",
        "fase": "Engajamento",
        "data": "06/10, terça, 14h",
        "publico": "Não aluno não engajado",
        "assunto": "Você sumiu…",
        "tom": "discreto",
        "preheader": "Trouxe um presente pra você voltar.",
        "blocks": [
            ("p", "Faz tempo que você não aparece por aqui."),
            ("p", "Talvez IA tenha deixado de ser prioridade pra você."),
            ("p", "Talvez você tenha parado de acompanhar as novidades porque parecia coisa demais mudando ao mesmo tempo."),
            ("p", "Ou talvez só tenha faltado tempo mesmo."),
            ("p", "E eu entendo."),
            ("p", "Nos últimos meses, esse mercado mudou rápido."),
            ("p", "Novos modelos. Novas ferramentas."),
            ("p", "Novas formas de automatizar trabalho, pesquisar, programar, organizar informação e resolver tarefas que antes levavam muito mais tempo."),
            ("p", "É muito fácil se perder."),
            ("p", "Mas se você ainda tem interesse em usar IA para ganhar tempo, automatizar sua rotina, trabalhar melhor ou construir projetos mais rápido, eu queria te dar um bom motivo para voltar."),
            ("p", "A gente liberou um presente muito especial:"),
            ("p", "Um guia gratuito com as 50 Melhores Skills do Claude."),
            ("p", "São 50 formas práticas de explorar melhor o Claude e sair do uso mais básico da ferramenta e realmente automatizar tarefas com IA."),
            ("cta", "Quero receber o guia com 50 Skills do Claude"),
            ("p", "É gratuito."),
            ("p", "E mesmo que você esteja há meses sem acompanhar nossos conteúdos, esse guia pode ser uma boa forma de entender o que mudou e voltar sem precisar começar do zero."),
            ("p", "Se IA ainda faz sentido pra você, pega o material."),
            ("p", "Tenho certeza que vai te ajudar."),
            ("p", "Abraços,"),
            ("sign", "Rodrigo Tadewald", "Cofundador da Asimov Academy"),
        ],
    },
    {
        "id": "em-005",
        "code": "EM-005",
        "fase": "Pré-captura",
        "data": "13/10, terça, 10h30",
        "publico": "Aluno Trilha",
        "assunto": "Convite Exclusivo para você!",
        "tom": "chamativo",
        "preheader": "Vem pra Black Friday da Asimov",
        "blocks": [
            ("p", "Como você já é aluno de uma Trilha da Asimov, queria que você soubesse antes de todo mundo."),
            ("p", "Vem aí a Black Friday da Asimov."),
            ("p", "Vamos revelar um desconto exclusivo no Vitalício, um acesso para sempre a todos os nossos cursos e a todos que ainda vamos lançar."),
            ("p", "Ela acontece numa live que vamos fazer no YouTube."),
            ("p", "E tem uma condição ainda mais especial pra quem já estuda com a gente."),
            ("p", "Ainda não dá pra contar qual é."),
            ("p", "Mas já dá pra dizer quando ela vai ser revelada: no dia 04 de novembro, às 19h."),
            ("p", "E para garantir sua vaga é essencial que você clique no botão abaixo."),
            ("cta", "Quero me cadastrar na Black"),
            ("p", "Também preparamos duas surpresas, e as duas só aparecem ao vivo."),
            ("p", "Uma são bônus que só existem pra quem estiver na live."),
            ("p", "A outra é o lançamento que os alunos mais pediram."),
            ("p", "Qual é, eu guardo pra noite do dia 04."),
            ("p", "A sua trilha é uma parte do catálogo."),
            ("p", "Se em algum momento você quis aprender mais sobre IA, vale acompanhar essa Black de perto."),
            ("p", "Quem se cadastra recebe os avisos da Black e, no dia da live, o link da transmissão."),
            ("cta", "Quero me cadastrar na Black"),
            ("p", "Um abraço,"),
            ("sign", "Rodrigo Tadewald", ""),
            ("ps", "Fique atento ao seu e-mail, vamos enviar muitos avisos importantes por aqui."),
        ],
    },
    {
        "id": "em-022",
        "code": "EM-022",
        "fase": "Captação",
        "data": "23/10, sexta, 11h",
        "publico": "Não aluno não engajado",
        "assunto": "Essa Black vai ser ao vivo",
        "tom": "chamativo",
        "preheader": "E tem um motivo pra isso...",
        "blocks": [
            ("p", "Black Friday de curso online costuma chegar do mesmo jeito: um cupom e um cronômetro na sua caixa de entrada."),
            ("p", "A da Asimov vai acontecer ao vivo."),
            ("p", "No dia 04/11, quarta-feira, às 19h, no YouTube."),
            ("p", "É nessa live que a gente revela um desconto exclusivo no acesso para sempre a todos os nossos cursos e a todos que ainda vamos lançar."),
            ("cta", "Quero me cadastrar na Black"),
            ("p", "E tem um motivo pra ser ao vivo."),
            ("p", "Na live, eu divido o palco com mais três experts da Asimov:"),
            ("ul", ["Juliano Faccioni, de análise de dados", "Samuel Sublate, de vibe coding", "Lucas Petry, da Formação AI Designer"]),
            ("p", "E só quem estiver assistindo vai ver o lançamento que os alunos mais pediram."),
            ("p", "Os bônus da transmissão também são só pra quem estiver lá."),
            ("p", "Quem se cadastra recebe o link oficial da live e fica sabendo de tudo primeiro."),
            ("cta", "Quero me cadastrar na Black"),
            ("p", "Um abraço,"),
            ("sign", "Rodrigo Tadewald", ""),
        ],
    },
]


def render_blocks(blocks, p, cta, ul, sign, ps):
    """Monta o corpo chamando os renderizadores do design system para cada tipo de bloco.

    Parágrafos seguidos ficam juntos; o espaço maior entra só em volta de botão, lista e assinatura.
    """
    out = []
    for kind, *args in blocks:
        out.append({"p": p, "cta": cta, "ul": ul, "sign": sign, "ps": ps}[kind](*args))
    return "".join(out)
