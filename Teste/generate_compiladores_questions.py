import pandas as pd
import os

def main():
    data = [
        {
            "Identificação da questão": "UA-02_QUESTÃO-1_OBJ-2_FÁCIL",
            "Palavra chave": "diagrama de estados",
            "Tipo da Questão": "questão de complementação Simples",
            "Nível cognitivo": "Reconhecimento",
            "Texto da Questão": (
                "Disciplina: Compiladores\n"
                "A modelagem de autômatos finitos determinísticos (AFDs) é frequentemente representada de forma gráfica por meio de diagramas de estados, facilitando a compreensão do fluxo de processamento de cadeias. Nessa representação, cada elemento gráfico possui um significado convencional estabelecido na teoria da computação. Por exemplo, o estado a partir do qual a leitura dos símbolos do alfabeto é iniciada é indicado graficamente por um __________ apontando para si. Em contrapartida, os estados finais, que definem a aceitação da cadeia de caracteres processada, são identificados visualmente no diagrama por meio de um __________"
            ),
            "Alternativa A": "triângulo; círculo menor dentro de outro círculo.",
            "Alternativa B": "quadrado; losango preenchido.",
            "Alternativa C": "círculo tracejado; retângulo com bordas arredondadas.",
            "Alternativa D": "triângulo; retângulo com bordas arredondadas.",
            "Questão correta": "a",
            "Feedback da questão": (
                "A resposta certa é triângulo; círculo menor dentro de outro círculo.\n"
                "Comentário: No diagrama de estados de um AFD, por convenção, o estado inicial q0 é indicado por um triângulo apontando para si, enquanto o estado final ou de aceitação é representado por um círculo duplo (um círculo menor dentro de outro círculo). "
                "Fonte: NASCIMENTO, L. B. G. Autômatos finitos determinísticos. Porto Alegre: SAGAH, p. 6-7."
            )
        },
        {
            "Identificação da questão": "UA-03_QUESTÃO-1_OBJ-2_FÁCIL",
            "Palavra chave": "aceitação no AFN",
            "Tipo da Questão": "questão de complementação Simples",
            "Nível cognitivo": "Reconhecimento",
            "Texto da Questão": (
                "Disciplina: Compiladores\n"
                "No estudo dos autômatos finitos não determinísticos (AFNs), a computação de uma cadeia de entrada pode percorrer múltiplos caminhos simultaneamente devido ao não determinismo das transições. Diferente do autômato determinístico, a determinação de sucesso no processamento de uma entrada em um AFN baseia-se em conjuntos de estados alcançados. Ao final do consumo de todos os símbolos da cadeia, a cadeia é considerada aceita pela máquina se, e somente se, a interseção entre o conjunto final de estados alcançados e o conjunto de estados finais (F) for __________"
            ),
            "Alternativa A": "não vazia (ou seja, contiver pelo menos um estado final).",
            "Alternativa B": "um conjunto vazio (indicando que nenhum estado final foi ativado).",
            "Alternativa C": "igual ao conjunto de todos os estados do autômato.",
            "Alternativa D": "composta exclusivamente por estados não alcançados.",
            "Questão correta": "a",
            "Feedback da questão": (
                "A resposta certa é não vazia (ou seja, contiver pelo menos um estado final).\n"
                "Comentário: A condição de aceitação em um AFN estabelece que a cadeia de entrada será aceita se, ao final do processamento, a interseção do conjunto final de estados alcançados com o conjunto de estados finais (F) for não vazia. "
                "Fonte: MACHADO, V. A. Linguagens formais e autômatos: autômatos finitos não determinísticos. Porto Alegre: SAGAH, p. 7."
            )
        },
        {
            "Identificação da questão": "UA-08_QUESTÃO-1_OBJ-2_MÉDIA",
            "Palavra chave": "conceito de decidibilidade",
            "Tipo da Questão": "Questão de Resposta Múltiplas",
            "Nível cognitivo": "Compreensão",
            "Texto da Questão": (
                "Disciplina: Compiladores\n"
                "Durante um seminário de Teoria da Computação, um grupo de estudantes analisa a relação entre a teoria das linguagens formais e a decidibilidade de problemas matemáticos. O palestrante explica que a solucionabilidade de um problema de decisão está fortemente acoplada à capacidade de uma Máquina de Turing (MT) atuar como decididora de linguagens. Para ilustrar esse comportamento, são apresentadas as classes de linguagens recursivas e recursivamente enumeráveis, destacando que a classificação de solucionabilidade de um problema depende do comportamento da MT diante de entradas que pertencem ou não à linguagem associada. Assim, a distinção entre esses conceitos é crucial para determinar os limites computacionais do que pode ser efetivamente solucionado.\n"
                "Com base nos conceitos de decidibilidade e na classificação de linguagens por meio de máquinas de Turing, a caracterização correta de uma linguagem recursiva e sua relação com os problemas solucionáveis estabelece que:"
            ),
            "Alternativa A": "a linguagem é recursiva se existe uma máquina de Turing que sempre para, indicando de forma explícita se a palavra de entrada pertence ou não a ela.",
            "Alternativa B": "os problemas parcialmente solucionáveis são equivalentes às linguagens recursivas, pois a máquina sempre para na rejeição.",
            "Alternativa C": "a classe das linguagens recursivamente enumeráveis define os problemas solucionáveis em que a máquina entra em loop infinito para respostas afirmativas.",
            "Alternativa D": "uma linguagem recursiva representa problemas completamente insolúveis em que a máquina de Turing é incapaz de parar para qualquer palavra fornecida.",
            "Questão correta": "a",
            "Feedback da questão": (
                "A resposta certa é a linguagem é recursiva se existe uma máquina de Turing que sempre para, indicando de forma explícita se a palavra de entrada pertence ou não a ela.\n"
                "Comentário: A classe dos problemas decidíveis (solucionáveis) é equivalente às linguagens recursivas. Para estas, existe uma MT decididora, ou seja, uma máquina que sempre para (aceitando ou rejeitando) para qualquer cadeia de entrada. "
                "Fonte: SILVA, F. R. Decidibilidade. Porto Alegre: SAGAH, p. 5-6."
            )
        },
        {
            "Identificação da questão": "UA-09_QUESTÃO-1_OBJ-2_MÉDIA",
            "Palavra chave": "estrutura de um compilador",
            "Tipo da Questão": "Questão de Resposta Múltiplas",
            "Nível cognitivo": "Compreensão",
            "Texto da Questão": (
                "Disciplina: Compiladores\n"
                "No projeto de sistemas de software de infraestrutura, a arquitetura clássica de um compilador é estruturada de forma modular para gerenciar a complexidade do mapeamento do código-fonte para o código-objeto final. Tradicionalmente, esse mapeamento divide-se em duas grandes macroetapas interdependentes, comumente denominadas análise (front-end) e síntese (back-end). A parte da análise divide o programa de origem e gera uma representação intermediária, que serve de entrada para a parte da síntese construir o código equivalente na linguagem de destino. Cada uma dessas partes desempenha papéis específicos e interage diretamente com uma estrutura de dados global compartilhada, conhecida como tabela de símbolos.\n"
                "Considerando a divisão estrutural de um compilador entre análise (front-end) e síntese (back-end), a responsabilidade específica atribuída à etapa de análise consiste em:"
            ),
            "Alternativa A": "decompor o programa de origem, impor uma estrutura gramatical e gerar a representação intermediária coletando informações na tabela de símbolos.",
            "Alternativa B": "traduzir a representação intermediária diretamente para a linguagem Assembly do hardware sem consultar a tabela de símbolos.",
            "Alternativa C": "realizar a junção dos diferentes arquivos de código-objeto gerados pelas bibliotecas externas em um único arquivo executável completo.",
            "Alternativa D": "ler os arquivos pré-processados e convertê-los diretamente em representações binárias sem a imposição de regras gramaticais.",
            "Questão correta": "a",
            "Feedback da questão": (
                "A resposta certa é decompor o programa de origem, impor uma estrutura gramatical e gerar a representação intermediária coletando informações na tabela de símbolos.\n"
                "Comentário: A parte da análise (front-end) do compilador divide o código de origem em partes, impõe uma estrutura gramatical, cria uma representação intermediária e gerencia os metadados na tabela de símbolos, repassando-os à fase de síntese. "
                "Fonte: ALVES, N. S. R. Introdução a compiladores. Porto Alegre: SAGAH, p. 5-6."
            )
        },
        {
            "Identificação da questão": "UA-05_QUESTÃO-1_OBJ-2_DIFÍCIL",
            "Palavra chave": "algoritmo de conversão MT",
            "Tipo da Questão": "Questão de Resposta Múltiplas com três sentenças combinadas",
            "Nível cognitivo": "Aplicação e Análise",
            "Texto da Questão": (
                "Disciplina: Compiladores\n"
                "No estudo dos limites da computabilidade, a equivalência entre as gramáticas irrestritas (Tipo 0 na Hierarquia de Chomsky) e as Máquinas de Turing (MT) é um resultado fundamental. A prova do teorema que estabelece que qualquer linguagem recursivamente enumerável L(M) pode ser gerada por uma gramática irrestrita L(G) envolve um algoritmo de conversão estruturado. Esse algoritmo constrói uma gramática G cujas produções simulam, de forma reversa, a computação da máquina M. Para tanto, a gramática utiliza três conjuntos de regras de produção específicos que geram formas sentenciais contendo marcadores de início (#), estados internos do autômato e símbolos de espaço em branco (□), permitindo a eliminação desses marcadores auxiliares na etapa final do processo de derivação.\n"
                "Com base nas regras do algoritmo de conversão de uma Máquina de Turing M para uma gramática irrestrita G semanticamente equivalente, analise as afirmativas a seguir:\n"
                "I. O primeiro conjunto de regras de produção (i) tem como objetivo gerar formas sentenciais da forma S ⇒* #xqf y, que correspondem à configuração de aceitação ou parada da máquina de Turing.\n"
                "II. O segundo conjunto de regras de produção (ii) é responsável por simular o avanço da computação no sentido direto da Máquina de Turing, partindo da configuração inicial #q0w até alcançar o estado final.\n"
                "III. O terceiro conjunto de regras de produção (iii) é composto por derivações (como #q0 → ε e □ → ε) projetadas para eliminar os marcadores auxiliares e símbolos de branco da forma sentencial na etapa final.\n"
                "Está correto o que se afirma em:"
            ),
            "Alternativa A": "apenas a afirmativa I.",
            "Alternativa B": "apenas as afirmativas I e III.",
            "Alternativa C": "apenas as afirmativas II e III.",
            "Alternativa D": "apenas a afirmativa II.",
            "Questão correta": "b",
            "Feedback da questão": (
                "A resposta certa é apenas as afirmativas I e III.\n"
                "Comentário: A afirmativa II está incorreta porque o segundo conjunto de regras de produção (ii) é responsável por simular a computação reversa da máquina de Turing (derivando a partir da parada #xqf y até a configuração inicial #q0w), e não o avanço direto. As afirmativas I e III descrevem corretamente as atribuições dos conjuntos de produções i e iii no algoritmo. "
                "Fonte: MACHADO, J. H. A. P. Gramáticas e máquina de Turing. Porto Alegre: SAGAH, p. 10-11."
            )
        }
    ]

    df = pd.DataFrame(data)
    
    xlsx_path = "/home/hamilcar/Antigravity/Teste/questoes_compiladores_UAs.xlsx"
    csv_path = "/home/hamilcar/Antigravity/Teste/questoes_compiladores_UAs.csv"
    
    df.to_excel(xlsx_path, index=False)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    
    print(f"Excel gerado em: {xlsx_path}")
    print(f"CSV gerado em: {csv_path}")

if __name__ == "__main__":
    main()
