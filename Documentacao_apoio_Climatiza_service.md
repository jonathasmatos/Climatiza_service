Especificação Técnica: Automação de Planos de Manutenção Preventiva e Gestão de Ativos

1. Visão Geral e Objetivos da Transformação Digital

A transição do modelo de controle manual, atualmente alicerçado em planilhas esparsas e registros em papel, para uma infraestrutura digital automatizada é um imperativo estratégico para a escalabilidade operacional da organização. A dependência excessiva da memória do setor administrativo para o mapeamento de visitas e frequências de limpeza de filtros compromete a eficiência, gerando gargalos no faturamento e riscos de falhas no agendamento. Esta automação visa substituir a triagem manual por um motor de regras inteligente, mitigando a perda de dados e assegurando que as obrigações contratuais sejam cumpridas sem desvios.

A mitigação de riscos é o ponto central desta transformação. Ao digitalizar o inventário e automatizar os gatilhos de manutenção, eliminamos a possibilidade de equipamentos serem negligenciados por erro humano. A transição para uma operação orientada a dados não apenas protege a integridade dos ativos dos clientes, mas também garante o respaldo financeiro da empresa através de registros precisos. Contudo, a eficácia desta inteligência depende fundamentalmente de uma arquitetura de dados hierárquica e rigorosa.

2. Arquitetura de Entidades e Hierarquia de Ativos

Para suportar a complexidade de clientes com múltiplas unidades e ambientes distintos, o sistema deve estruturar os dados de forma relacional e hierárquica. Esta modelagem permite uma visão granular de cada ativo, facilitando a gestão de contratos de manutenção (PMOC) e o histórico de intervenções.

Relacionamento e Cardinalidade:

* Cliente (1:N) Local/Filial: Um cliente centraliza múltiplas unidades físicas (ex: Cliente Tok com unidades Logtop e Galpão).
* Local (1:N) Ambiente: Cada unidade possui setores específicos (ex: Escritório, Diretoria, Academia).
* Ambiente (1:N) Equipamento: Os ativos são individualizados por ambiente para localização exata.
* Ordem de Serviço (1:N) Equipamento: Uma única OS pode contemplar a manutenção de múltiplos equipamentos dentro de um mesmo ambiente ou local.

Atributos Obrigatórios do Ativo:

Atributo	Especificação / Exemplos
Marca	Agratto, Gree, TCL, Midea, Philco, Admiral, Springer.
Tipo / Linha	Split, Piso Teto, Cassete.
Capacidade (BTUs)	9k, 12k, 18k, 22k, 24k, 28k, 30k, 36k, 55k, 60k.
Localização	Nome do Ambiente (ex: Sala Sr. Paulo, Galpão, Copa).
Elétrica / Estética	Voltagem (ex: 220V) e Cor (Padrão: Branca).

Uma vez consolidado o inventário, o sistema está apto a processar as regras de recorrência que alimentam o motor de automação.

3. Lógica de Automação e Geração de Cronogramas

A lógica "set and forget" (configurar e esquecer) é o núcleo da inteligência administrativa. O sistema deve processar os termos contratuais para gerar demandas preventivas de forma autônoma, eliminando a necessidade de conferência manual de datas.

Regras do Motor de OS:

* Configurar: Estabelecer a periodicidade por serviço (ex: limpeza de filtros a cada 30 dias ou manutenção preventiva trimestral).
* Vincular: Associar contratos de manutenção a múltiplos locais de um cliente simultaneamente.
* Disparar: Abertura automática da OS preventiva no mês correspondente, baseada na data da última visita concluída ou na configuração específica do plano de manutenção.
* Alertar: Notificações automáticas ao administrativo para planejamento de rota e à equipe técnica para execução imediata.

Este fluxo garante que a demanda chegue ao campo de forma estruturada, iniciando o ciclo de vida operacional da Ordem de Serviço.

4. Fluxo Operacional da Ordem de Serviço (OS) Digital

A OS Digital é o núcleo da prestação de serviço, rastreando o atendimento desde a identificação do problema até o encerramento administrativo.

Fluxo de Estados (Lifecycle):

* Aberta / Em Orçamento: Triagem inicial; o administrativo define valores de mão de obra e insumos com base na capacidade da máquina (9k a 60k BTUs).
* Agendada: Alocação de técnicos e definição de data para execução.
* Em Execução: Coleta de dados em campo, diagnóstico técnico e registro de intervenções.
* Aguardando Peças (SLA Pause): Status de pendência obrigatório para casos de garantia (ex: aguardando envio de compressor por fabricantes como Agratto, Gree ou TCL). Este estado pausa o SLA de conclusão.
* Execução Concluída: Trabalho técnico finalizado, com envio obrigatório de laudo e evidências fotográficas via sistema.
* Encerrada: Fechamento administrativo realizado após emissão da NF e validação da prestação de contas.

A transição entre esses estados exige protocolos de validação rigorosos para garantir a salvaguarda técnica da empresa.

5. Protocolos de Validação e Salvaguarda Técnica

A documentação digital não é mera burocracia, mas uma proteção jurídica contra contestações. O "So What?" desta obrigatoriedade é claro: sem evidências, a empresa fica vulnerável a custos de garantias negadas por erro de terceiros.

O Caso TCL e a Proteção Jurídica: O registro fotográfico é mandatório para combater a manipulação por terceiros. No caso TCL citado no contexto, a galeria de fotos provou que a instalação original estava correta, desmentindo laudos de outras assistências que alegavam inversão de cabos. Além disso, as fotos protegem contra acusações de danos estruturais (como telhados quebrados) ocorridos durante obras simultâneas no local do cliente.

Checklist Digital de Instalação (Interface Técnica):

* [ ] Tamanho da tubulação está de acordo com o manual?
* [ ] Pressão do fluido refrigerante conferida?
* [ ] Distância técnica: Condensador ao teto validada?
* [ ] Distância técnica: Evaporador ao teto validada?
* [ ] O produto possui algum erro de instalação prévia por terceiros?
* [ ] Registro fotográfico do cabeamento e ambiente anexado?

6. Gestão de Insumos, Logística e Prestação de Contas

A saúde financeira da operação depende do controle milimétrico de deslocamentos e materiais aplicados, especialmente em atendimentos de fabricantes credenciadas.

Controle Logístico e KM: O campo "KM Percorrido" (ida e volta) é de preenchimento obrigatório no encerramento da OS. Esta informação é o requisito fundamental para o reembolso de deslocamento junto às fabricantes Agratto, Gree e TCL. Sem este dado, o faturamento da garantia é inviabilizado.

Lista de Verificação de Insumos (Materiais): No momento do orçamento e da separação física para a equipe, o sistema deve gerenciar os seguintes itens:

* Cabo PP (metragem e integridade).
* Tubulação de Cobre (diâmetro e comprimento).
* Fita Blackout para acabamento.
* Fluidos refrigerantes e componentes específicos (ex: compressores).

Este controle assegura que a rentabilidade do contrato seja preservada e que os materiais orçados coincidam com o consumo real em campo.

7. Templates de Saída e Relatórios Dinâmicos

A etapa final do processo é a transformação dos dados coletados em documentos de saída que atendam às diferentes necessidades dos stakeholders.

Lógica de Templates Dinâmicos:

* Relatório de Prestação de Contas (Fabricante): Template configurável que espelha os campos oficiais das marcas (ex: layout Agratto). Deve consolidar checklist técnico, laudo de diagnóstico, componentes trocados, KM percorrido e o dossiê fotográfico para validação da garantia.
* Dossiê de Histórico do Cliente: Focado no "Histórico Vital" do ativo. Permite que, ao consultar um cliente, o administrativo acesse instantaneamente instalações anteriores, datas de manutenção e fotos, facilitando orçamentos reativos e preventivos.

Esta arquitetura integra todas as pontas da operação, transformando a gestão de manutenção em um processo transparente, auditável e focado na maximização da rentabilidade através de dados.



Guia de Fluxo de Trabalho: O Ciclo de Vida do Atendimento em Climatização

1. Introdução: A Sinergia entre o Técnico e o Administrativo

O sucesso sustentável de uma empresa de climatização não repousa apenas na destreza técnica de sua equipe de campo, mas na sinergia absoluta entre a execução do serviço e a gestão do Back-office. A "conversa" entre o que ocorre no cliente e o registro no escritório é o que diferencia o amadorismo do profissionalismo de alto nível. Este guia foi desenhado para transformar o fluxo operacional em uma sequência lógica, garantindo que a informação flua sem ruídos, transformando o caos de ordens esparsas em um processo auditável, rentável e seguro.


--------------------------------------------------------------------------------


2. Fase 1: Mapeamento de Demanda, Orçamento e Agendamento

O ciclo de vida do atendimento inicia-se no levantamento de dados. Antes de qualquer deslocamento, o consultor deve realizar o Mapeamento de Demanda para alinhar a infraestrutura necessária. É vital identificar a categoria do serviço (instalação vs. manutenção) e a carga térmica exata.

Abaixo, a relação técnica de capacidades e insumos, integrando as marcas que compõem o portfólio de credenciamento da empresa:

Capacidade (BTUs)	Modelos Frequentes (Exemplos)	Materiais Básicos Necessários
9.000 a 12.000	Split High Wall (Gree, Midea, Philco)	Tubulação de cobre, Isolamento, Cabo PP, Fita Blackout
18.000 a 24.000	Split / Cassete (Gree, Admiral, Springer)	Tubulação de maior bitola, fiação reforçada, Fita Blackout
28.000 a 36.000	Piso Teto / Cassete (Gree, TCL, Agratto)	Suportes industriais, carga de fluido refrigerante, fita blackout
36.000 a 55.000	Piso Teto / Cassete (TCL, Gree)	Materiais robustos, suportes de alta carga, verificação de rede trifásica

Os 3 Elementos Fundamentais do Agendamento: Para a segurança financeira e operacional, o serviço só avança após o alinhamento de:

1. Valor da Mão de Obra: Precificado conforme a complexidade técnica.
2. Valor do Material: Incluindo tubos, cabos e consumíveis (ex: fita blackout).
3. Data e Hora: Compromisso formalizado para otimização da rota.


--------------------------------------------------------------------------------


3. Fase 2: A Ordem de Serviço (O.S.) como Documento de Credenciamento

A Ordem de Serviço (O.S.) transcende o papel de recibo; ela é um documento técnico de gestão e a base para manter o Credenciamento junto a fabricantes como Agratto, Gree e TCL. Uma O.S. mal preenchida pode invalidar garantias e gerar prejuízos jurídicos.

Campos obrigatórios baseados no padrão técnico de excelência:

* Dados do Consumidor: Identificação completa e localização.
* Dados do Produto: Linha (Split, Piso Teto, Cassete), Modelo, Voltagem e Cor.
* Métricas de Instalação: Tamanho da Tubulação, Pressão do Sistema, Distância da Condensadora ao Teto e Distância da Evaporadora ao Teto.
* Linha do Tempo: Datas da 1ª visita, 2ª visita e data de encerramento.
* Descrição Detalhada: Registro de diagnóstico (ex: "identificado cabo PP rompido" ou "baixa pressão de fluido").
* Controle de Custos: Registro de KMs Percorridos para cálculo do custo operacional real.


--------------------------------------------------------------------------------


4. Fase 3: Registro Fotográfico e a Proteção contra Manipulação de Terceiros

As evidências visuais são o "escudo" da empresa. O caso real da TCL exemplifica essa necessidade: após uma instalação perfeita, uma assistência técnica terceira alegou "inversão de cabos" para negar a garantia ao cliente. Apenas o registro fotográfico rigoroso pode provar que não houve manipulação de terceiros após a saída da sua equipe.

Checklist de "Melhores Práticas" Fotográficas:

* [ ] Estado Inicial: Comprovação da integridade do local antes do início.
* [ ] Infraestrutura e Conexões: Fotos macro de conexões elétricas (cabos PP) e soldas de tubulação.
* [ ] Parâmetros Técnicos: Foto do manômetro comprovando a pressão registrada na O.S.
* [ ] Segurança de Entorno: Fotos de telhados, forros e estruturas vizinhas para evitar cobranças indevidas por danos causados por outros profissionais (pedreiros, eletricistas).
* [ ] Entrega Final: Equipamento montado, ambiente limpo e teste de dreno realizado.


--------------------------------------------------------------------------------


5. Fase 4: Encerramento, Faturamento e Recorrência

Com a execução concluída, o fluxo retorna ao administrativo para o fechamento financeiro. Em casos de troca de componentes complexos, como compressores, a O.S. deve monitorar todo o trâmite de solicitação da peça junto à fabricante até a reinstalação final.

* Consolidação Financeira: O valor final da mão de obra é consolidado, a assinatura do cliente é coletada e os dados são enviados à central para emissão da Nota Fiscal.
* Gestão de Contratos de Manutenção: O encerramento de um serviço é a porta de entrada para a manutenção preventiva.

Exemplo de Gestão de Carteira: Unidades como a Tok, Logitop e o Galpão (que operam com máquinas Midea, Springer e Gree de diversas capacidades) exigem um cronograma de limpeza de filtros e revisão periódica. Ao registrar esses dados no sistema, o "Manual" se torna automático, permitindo que o administrativo antecipe a necessidade do cliente e garanta receita recorrente.


--------------------------------------------------------------------------------


6. Conclusão: O Checklist do Sucesso

Para garantir que o ciclo de vida do atendimento seja cumprido com maestria operacional, memorize os 5 pilares:

1. Diagnóstico Prévio: Identifique BTUs e marcas (Gree, TCL, Midea) antes da saída.
2. Rigor Documental: Preencha todos os campos da O.S., incluindo pressões e distâncias de teto.
3. Segurança Jurídica: Use fotos para blindar a empresa contra alegações de "manipulação de terceiros".
4. Encerramento Ágil: O envio imediato dos dados para o back-office garante o faturamento sem atrasos.
5. Fidelização: Transforme atendimentos pontuais em contratos de manutenção preventiva.

"A foto é o escudo do técnico contra reclamações de telhas quebradas ou fiações adulteradas por terceiros."

"O lucro de uma empresa de climatização nasce na técnica, mas sobrevive na precisão do seu registro administrativo."




Gestão de Climatização e Fluxos de Atendimento Multimarcas
(As respostas salvas são somente para visualização)
Embora a empresa seja credenciada oficialmente apenas para três fabricantes (Agratto, Gree e TCL)
, os registros de inventário mostram que ela também atende e gerencia equipamentos de diversas outras marcas não credenciadas, como Philco, Admiral, Springer e Midea
.
Para lidar com esses equipamentos, o sistema adaptaria o fluxo de atendimento da seguinte forma:
Mapeamento e Inventário Unificado: Os aparelhos de marcas não credenciadas seriam cadastrados no sistema normalmente. Eles seriam vinculados ao cliente, ao local físico (ex: Galpão, loja Logtop), ao ambiente exato (ex: Academia, Sala de Reunião), à marca e à capacidade térmica em BTUs, participando ativamente dos planos de manutenção preventiva e limpeza de filtros
.
Ordem de Serviço Interna (Padrão): Em vez de acionar os templates específicos de prestação de contas exigidos para as garantias das fabricantes (como o formulário detalhado da Agratto)
, o sistema utilizaria uma Ordem de Serviço padrão da própria empresa para registrar o atendimento.
Orçamento e Faturamento Direto ao Cliente: Como não há o acionamento de garantia de fábrica para envio de peças de reposição (como compressores)
, todo o escopo do serviço — incluindo valor da mão de obra e materiais utilizados (cabos, cobre, fita blackout) — seria orçado e cobrado integralmente do consumidor final, finalizando com a emissão da nota fiscal
.
Obrigatoriedade das Fotos Mantida: A exigência de registrar fotos de tudo o que foi executado continuaria sendo estritamente obrigatória
. O envio das fotos não serviria para prestação de contas à fabricante, mas sim como o respaldo fundamental da empresa para provar como o serviço foi entregue, protegendo os técnicos contra acusações de danos estruturais no local (como telhados quebrados por outros profissionais) ou manipulação de terceiros na instalação
.

Gestão Centralizada de Históricos e Manutenções Preventivas
(As respostas salvas são somente para visualização)
No novo sistema, a recuperação do histórico de manutenções deve ocorrer de forma rápida e centralizada a partir de uma busca pelo cadastro do cliente.
De acordo com o relato da administração, o fluxo ideal funcionará da seguinte maneira: quando um cliente entrar em contato novamente (por exemplo, quando já tiver passado o período de instalação e ele quiser agendar uma manutenção preventiva), o atendente precisará apenas digitar o nome ou os dados desse cliente no sistema
.
Ao fazer isso, a plataforma resgatará automaticamente a ficha do cliente, tornando muito mais prático visualizar o histórico de serviços. O sistema exibirá, por exemplo, que determinado cliente realizou uma instalação em uma data específica, indicando que agora é o momento exato para a manutenção
.
Do ponto de vista da modelagem do banco de dados (conforme estruturado anteriormente), essa facilidade ocorrerá porque as Ordens de Serviço (OS) antigas não serão descartadas, mas sim armazenadas e vinculadas permanentemente ao ID_Cliente e ao ID_Equipamento. Isso garantirá que todo o histórico técnico — incluindo a data da instalação, os diagnósticos passados, as peças que já foram trocadas e as fotos dos atendimentos anteriores — fique imediatamente acessível na tela assim que o cliente for consultado.



Gestão e Prestação de Contas para Assistências Técnicas Credenciadas
(As respostas salvas são somente para visualização)
Com base nos materiais fornecidos, o sistema poderia gerar Relatórios de Prestação de Contas (ou Encerramento de OS) específicos para o envio às fabricantes (como Agratto, Gree e TCL) para as quais a empresa atua como credenciada
.
Como cada fabricante exige um modelo diferente para validar os atendimentos em garantia e autorizar pagamentos, o sistema poderia gerar relatórios dinâmicos contendo os seguintes elementos:
Templates Específicos por Marca: Relatórios formatados para espelhar as exigências de cada fabricante, como o formulário da Agratto, que exige o preenchimento de um checklist técnico de instalação (tamanho da tubulação, pressão, distância do teto para o condensador e evaporador, e checagem de erros de instalação prévios)
.
Dados do Consumidor e do Equipamento: Identificação do cliente e as características exatas da máquina atendida, como linha (split, piso teto, cassete), modelo, voltagem e cor
.
Laudo Técnico: O registro das datas das visitas e a descrição detalhada do diagnóstico e serviço realizado (ex: "cabo PP rompido" ou "baixa de fluido refrigerante")
.
Custos e Peças para Reembolso: A relação exata dos componentes trocados (como compressores enviados pela fábrica) e o valor da mão de obra
.
Relatório de Quilometragem: A consolidação dos KMs percorridos pela equipe no deslocamento de ida e volta, uma informação que é obrigatoriamente enviada para a fabricante no momento de encerrar o serviço e prestar contas
.
Dossiê Fotográfico (Respaldo de Garantia): Um relatório anexo gerado com todas as fotos capturadas durante o atendimento, que são enviadas à fabricante junto com a Ordem de Serviço
. Esse dossiê visual atua como a prova definitiva do estado em que o equipamento e o local foram deixados, servindo para aprovar garantias e proteger a empresa contra acusações de manipulação de terceiros (como relatado em um atendimento da marca TCL) ou danos estruturais no local da obra
.


Modelagem de Sistema para Gestão de Atendimentos Técnicos
(As respostas salvas são somente para visualização)
Com base nos materiais fornecidos, aqui está a análise estruturada para a modelagem do sistema de gestão de atendimentos técnicos:
1. Estrutura do negócio
Atores envolvidos:
Cliente / Consumidor final: Quem possui os equipamentos e solicita os serviços
.
Administrativo: O responsável por receber a demanda, passar orçamentos, agendar serviços com a equipe, fazer pedidos de peças aos fabricantes e emitir a nota fiscal
.
Técnico (referido como "os meninos"): Quem se desloca até o cliente, executa o serviço (instalação ou manutenção), faz os registros fotográficos e passa o status de conclusão
.
Fabricante: Marcas (como Agratto, Gree e TCL) para as quais a empresa atua como credenciada, fornecendo peças de reposição em garantia
.
Quem solicita atendimento: O cliente, geralmente através de e-mail ou telefone
.
Quem agenda serviços: O administrativo, após aprovação de orçamentos e definição dos materiais que serão utilizados
.
Quem executa manutenção: Os técnicos em campo
.
Quem registra ou fecha a ordem de serviço: O técnico informa a conclusão e envia as fotos, mas é o administrativo que encerra o atendimento formalmente no sistema/planilha e emite a nota fiscal
.
2. Estrutura de clientes
Organização dos clientes: Há clientes avulsos e clientes com contratos/planos de manutenção
.
Múltiplos locais/ambientes: Um mesmo cliente pode possuir múltiplos endereços físicos (ex: Lojas Tok, Logtop e um Galpão)
.
Distribuição de equipamentos: Dentro de cada local, existem subdivisões em ambientes ou setores (ex: Escritório, Diretoria, Copa, Sala de Reunião, RH) onde os equipamentos são mapeados individualmente de forma manual
.
3. Inventário de equipamentos
O sistema atual (manual e em planilhas) armazena os seguintes dados sobre o parque de equipamentos dos clientes:
Marca/Fabricante: Exemplos incluem Gree, Agratto, Philco, Admiral, Springer, Midea e TCL
.
Modelo/Linha: Split, Piso Teto, Cassete
.
Capacidade térmica: Registrada em BTUs, variando desde 9k até 60k (ex: 12k, 18k, 22k, 24k, 30k, 36k, 55k)
.
Localização exata: Ambiente específico (ex: Sala Logtop, Sala Sr. Paulo, Galpão, Academia, Salão)
.
Outras especificações: Voltagem e Cor (sendo a cor geralmente branca)
.
4. Processo de atendimento (Fluxo Passo a Passo)
Solicitação do cliente: Contato via e-mail solicitando instalação ou informando um problema (ex: para manutenções ou garantias)
.
Orçamento e triagem: O administrativo alinha a capacidade da máquina (ex: 9k a 36k BTUs) para estipular o valor da mão de obra e levantar os materiais necessários (cabos, cobre, blackout, etc.)
.
Agendamento: Após o repasse e aprovação de valores, o serviço é agendado com o cliente e repassado aos técnicos
.
Envio do técnico: A equipe técnica vai ao local com o escopo do serviço e os materiais separados
.
Execução e diagnóstico: Os técnicos executam o serviço ou identificam o problema (ex: "cabo PP rompido" ou "baixa de fluido refrigerante")
.
Pausa para peças (se aplicável): Se houver necessidade de peças como compressores, o serviço é pausado até o fabricante enviar a peça
.
Registro fotográfico e conclusão: Os técnicos finalizam, tiram fotos detalhadas de tudo (equipamento, ambiente, telhados, estado das instalações) e avisam o administrativo
.
Encerramento da Ordem de Serviço: O administrativo emite a nota fiscal para o cliente (ou envia a OS e fotos para o fabricante) e encerra o ciclo
.
5. Informações registradas pelo técnico
Durante e após a visita, o técnico precisa fornecer:
Diagnóstico técnico: A causa raiz do problema
.
Descrição detalhada do serviço: Relato do que foi executado na máquina
.
Peças utilizadas/trocadas: Descrição de todos os componentes substituídos (ex: compressor) e materiais gastos na instalação
.
Dados de instalação técnica: Tamanho da tubulação, pressão, distância do condensador ao teto e do evaporador ao teto, e checagem de erros prévios de instalação
.
Logística: Quilometragem percorrida
.
Fotografias: Item estritamente obrigatório. Fotos de todo o ambiente, estado da obra, telhado e cabeamentos, para servir de respaldo contra acusações de danos ao local ou problemas de garantia
.
6. Estrutura das ordens de serviço (Exemplo de Formulário)
Com base no formulário físico da fabricante Agratto, a OS contém os seguintes campos
:
Identificação: Dados da Autorizada (CNPJ, Razão Social), Número da OS.
Consumidor: Nome, Endereço, CEP, Cidade, Estado, Telefone.
Produto: Linha (Split, Piso Teto, Cassete), Modelo, Voltagem, Cor.
Datas Operacionais: Data da 1ª visita, Data da 2ª visita, Data do encerramento.
Checklist de Instalação: Tamanho da Tubulação, Pressão, Distâncias do Teto (Condensador e Evaporador) e uma marcação de "O produto possui algum erro de instalação? (Sim/Não)".
Descrição do Serviço: Campo de texto livre para diagnóstico/ação.
Custos: Valor da mão de obra, KMs percorridos, Componentes Trocados e Valor Total (R$).
Validação: Assinaturas do cliente final e do assistente técnico.
7. Entidades principais do sistema
Para a modelagem do software, as entidades sugeridas são:
Cliente: Dados gerais e de cobrança.
Local / Filial: Endereços físicos vinculados a um cliente.
Ambiente: Cômodos ou setores dentro de um local.
Equipamento: A máquina de refrigeração propriamente dita.
Contrato de Manutenção: Regras de visitas periódicas.
Ordem de Serviço (OS): O documento principal que centraliza a execução do trabalho.
Técnico: O colaborador designado.
Material / Peça: Inventário de insumos (cabo, cobre, compressores).
Galeria / Anexo Fotográfico: Entidade para armazenar as fotos associadas à OS.
8. Identifique relações entre essas entidades
Um Cliente possui 1 ou N Locais
.
Um Local possui 1 ou N Ambientes
.
Um Ambiente abriga 1 ou N Equipamentos
.
Um Equipamento possui especificações de uma Fabricante
.
Uma Ordem de Serviço está vinculada a 1 Cliente e pode cobrir 1 ou N Equipamentos
.
Uma Ordem de Serviço é executada por 1 ou N Técnicos
.
Uma Ordem de Serviço consome N Materiais/Peças
.
Uma Ordem de Serviço deve conter N Anexos Fotográficos
.
9. Fluxo de estados para uma ordem de serviço
Solicitada / Aberta: O cliente realizou o pedido
.
Em Orçamento: Administrativo definindo valores e materiais necessários
.
Agendada: Serviço aprovado, alocado para uma equipe técnica e com data marcada
.
Em Execução: Técnicos em campo realizando visitas/diagnósticos
.
Aguardando Peças: Status suspensivo caso falte alguma peça (ex: compressor da garantia)
.
Execução Concluída: O técnico finalizou o trabalho físico, enviou o laudo e as fotos obrigatórias para o administrativo
.
Encerrada: Administrativo emitiu a nota fiscal, repassou informações para o credenciado (quando em garantia) e finalizou o processo
.
10. Modelo Conceitual Inicial
Um esboço lógico relacional baseado nos requisitos:
Tabela Clientes: ID_Cliente, Nome, Contato, Email, Plano_Manutencao_Ativo.
Tabela Enderecos_Locais: ID_Local, ID_Cliente, Nome_Local (ex: Loja Logtop, Galpão), Logradouro.
Tabela Ambientes: ID_Ambiente, ID_Local, Nome_Ambiente (ex: Diretoria, Sala de Reunião).
Tabela Equipamentos: ID_Equipamento, ID_Ambiente, Marca, Linha (Split, Cassete, Piso Teto), Modelo, BTUs, Voltagem, Cor.
Tabela Ordem_Servico: ID_OS, ID_Cliente, ID_Equipamento (se for serviço unificado em uma máquina), Status_Atual, Descricao_Problema, Data_1a_Visita, Data_Encerramento, Diagnostico_Tecnico, Km_Percorrido, Valor_Mao_Obra.
Tabela Checklist_Tecnico: ID_Checklist, ID_OS, Tamanho_Tubulacao, Pressao, Distancia_Condensador, Distancia_Evaporador, Erro_Instalacao_Previa.
Tabela OS_Materiais: ID_OS, Item (Peça ou Insumo), Quantidade.
Tabela OS_Fotos: ID_Foto, ID_OS, URL_Arquivo, Descricao (ex: "Foto do cabeamento finalizado", "Foto do telhado"). Permite a busca pelo histórico vital exigido para resolver contestações de garantias
.
Tabela Historico_OS_Equipamento: Um relacionamento para permitir que ao digitar os dados do cliente o sistema resgate instantaneamente manutenções anteriores
.


Protocolo de Registro e Controle de Materiais Técnicos
(As respostas salvas são somente para visualização)
O registro de materiais, como cabos e cobre, ocorre em diferentes etapas do processo de atendimento:
Fase de Orçamento e Agendamento: Durante o contato inicial, o setor administrativo alinha as características do serviço com o cliente (como a capacidade da máquina de ar-condicionado) e já discrimina todos os materiais que serão necessários para a execução, incluindo cabos, cobre e fita blackout
. O custo desses materiais é somado ao valor da mão de obra e repassado ao cliente para aprovação
.
Separação pela Equipe Técnica: Com o orçamento aprovado e o serviço agendado, a equipe técnica é informada sobre o escopo do trabalho (por exemplo, uma instalação com tubulação de até 3 metros). Com base nessa informação, os técnicos já sabem exatamente quais materiais devem separar no estoque para levar ao local
.
Registro na Ordem de Serviço (OS): Durante o atendimento, se houver necessidade de troca de peças ou materiais (como a identificação de um cabo PP rompido, por exemplo), isso deve ser detalhado por escrito
. O formulário físico de Ordem de Serviço possui um campo específico chamado "Componentes Trocados", onde os materiais substituídos ou utilizados são formalmente registrados para controle e faturamento
.


Registro Fotográfico como Salvaguarda Técnica e Jurídica
(As respostas salvas são somente para visualização)
As fotos funcionam como a prova principal do estado em que os técnicos deixaram o equipamento e o local de instalação, servindo de respaldo para a empresa frente a contestações
.
Elas auxiliam nas disputas de garantia e em problemas diários das seguintes formas:
Comprovação contra manipulação de terceiros: Em um caso envolvendo um equipamento da TCL, após a máquina dar problema, uma outra assistência técnica foi ao local, alegou que os cabos estavam invertidos e tentou negar a garantia do cliente
. Como os técnicos possuíam o registro fotográfico da instalação original finalizada, a empresa pôde comprovar que não houve erro de instalação e que o equipamento sofreu manipulação posterior por outras pessoas
.
Proteção contra acusações de danos estruturais: Em locais que estão passando por obras com outros profissionais envolvidos (como pedreiros), as fotos protegem os técnicos de serem responsabilizados por acidentes no ambiente, como a quebra de telhados
.
Por causa dessas situações, é uma ordem obrigatória da empresa que os técnicos tirem fotos de tudo o que foi executado durante o atendimento, registrando exatamente como o serviço foi entregue, para garantir o respaldo tanto da empresa quanto dos próprios profissionais
.


Automação do Mapeamento e Gestão de Manutenção Preventiva
(As respostas salvas são somente para visualização)
Atualmente, o mapeamento de visitas mensais para clientes com planos de manutenção é realizado de forma totalmente manual pelo setor administrativo
. O processo funciona da seguinte maneira:
Levantamento de Locais e Equipamentos: A empresa identifica todos os endereços físicos do cliente que fazem parte do plano (por exemplo, diferentes lojas como Tok, Logtop e um Galpão) e mapeia a quantidade de equipamentos de ar-condicionado (como splits) presentes em cada unidade
.
Detalhamento por Ambiente: É feito um registro em papel ou planilha especificando o modelo da máquina, a capacidade térmica (BTUs) e a sala exata onde ela está instalada dentro de cada filial (como Escritório, Diretoria, Copa, Academia, etc.)
.
Definição do Cronograma: Com base nesse inventário detalhado, o setor administrativo define a demanda do plano de manutenção, estipulando quantas vezes a equipe técnica precisará visitar o cliente por mês e qual será a frequência de serviços específicos, como a limpeza de filtros
.
Como o controle hoje exige muito esforço manual e não está integrado ao sistema atual da empresa, um dos requisitos desejados para o novo software é justamente uma ferramenta onde seja possível inserir e gerenciar esse mapeamento de forma automatizada
.


Gestão e Automação de Planos de Manutenção Multilocalidades
(As respostas salvas são somente para visualização)
O plano de manutenção para clientes com múltiplos locais é gerenciado atualmente de forma totalmente manual pelo setor administrativo
. O processo funciona da seguinte maneira:
Mapeamento de Locais: A empresa identifica todas as unidades físicas do cliente que fazem parte do plano de manutenção (como, por exemplo, as filiais Tok, Logtop e um Galpão)
.
Inventário por Ambiente: Para cada um desses locais, é feito um levantamento detalhado em papel, listando o ambiente exato onde cada ar-condicionado está instalado (como Escritório, Diretoria, Sala de Reunião ou Copa), a marca/modelo do equipamento (Gree, Agratto, Midea, etc.) e a sua capacidade térmica em BTUs
.
Definição da Demanda: Com esse mapeamento em mãos, o administrativo define o cronograma e a demanda do plano, estipulando quantas vezes a equipe técnica precisará visitar cada local por mês e qual será a periodicidade de tarefas específicas, como a limpeza dos filtros dos equipamentos
.
Como esse controle exige muito esforço manual e o sistema atual não parece oferecer um recurso adequado para isso, a criação de uma funcionalidade que automatize a inserção e gestão desse mapeamento é apontada como uma necessidade ideal para o novo sistema
.


Fluxo de Gestão e Alertas de Peças Pendentes
(As respostas salvas são somente para visualização)
Os materiais fornecidos não detalham um sistema automatizado de "alertas", mas descrevem claramente o fluxo operacional que ocorre quando uma peça precisa ser trocada (como um compressor na garantia). Em um sistema de gestão, isso funcionaria através de um status de pendência ou pausa na Ordem de Serviço (OS).
O processo para a troca de peças funciona da seguinte maneira:
Identificação do problema: Durante a visita, o técnico diagnostica que a máquina não funciona devido a uma peça defeituosa (por exemplo, um compressor estragado)
.
Solicitação ao fabricante: Como a empresa é credenciada, o setor administrativo aciona a fabricante (como Agratto, Gree ou TCL) e solicita o envio da peça de reposição
.
Pausa no atendimento (Status "Aguardando Peça"): A Ordem de Serviço não é encerrada. Ela é mantida aberta no sistema enquanto a empresa aguarda o fabricante enviar o componente
. Um "alerta" no sistema serviria para sinalizar que aquela OS está paralisada dependendo da chegada desse material.
Retomada e encerramento: Assim que a peça é recebida e instalada, os técnicos finalizam o serviço, o administrativo registra as informações finais (como quilometragem percorrida e valor) e a OS é, então, encerrada
.
Portanto, o alerta funcionaria como um controle de pendência, avisando ao administrativo quais Ordens de Serviço estão paradas aguardando o retorno e o envio de materiais por parte dos fabricantes
.


Automação de Cronogramas e Planos de Manutenção Preventiva
(As respostas salvas são somente para visualização)
Com base nos materiais analisados, atualmente o cronograma para a limpeza de filtros e visitas de manutenção é feito de forma totalmente manual pelo setor administrativo
. A responsável relata que faz o mapeamento das demandas (quantas vezes a equipe vai ao local no mês e quantas vezes faz a limpeza de filtros) manualmente, pois o sistema financeiro que utilizam hoje não possui ou não foi configurado para essa função
.
Para automatizar esse cronograma no novo sistema que está sendo modelado, a responsável mencionou que seria "perfeito" ter uma ferramenta específica para inserir esses dados
. Na prática da modelagem de software, essa automação funcionaria da seguinte forma:
Cadastro do Plano de Manutenção: O sistema deve ter um módulo onde o administrativo insere os termos do contrato do cliente, vinculando os múltiplos locais (como as lojas Tok, Logtop e o Galpão)
.
Mapeamento de Equipamentos: Dentro desse plano, cadastra-se o inventário exato de máquinas, especificando os ambientes (ex: Escritório, Diretoria, Salão) e as capacidades de cada ar-condicionado
.
Configuração da Periodicidade: O sistema deve permitir configurar a frequência de cada serviço (por exemplo, "limpeza de filtros a cada 30 dias").
Geração Automática de Demandas: Com esses dados preenchidos, o sistema passaria a gerar automaticamente as Ordens de Serviço preventivas nos meses correspondentes, alertando o setor administrativo e a equipe técnica de que a limpeza de filtros de determinados locais e ambientes está programada para aquele período, eliminando o controle em papel
.


Diretrizes para Gestão de Quilometragem em Ordens de Serviço
(As respostas salvas são somente para visualização)
O gerenciamento da quilometragem percorrida pelos técnicos no sistema deve seguir o fluxo de encerramento da Ordem de Serviço (OS):
Registro no Encerramento do Serviço: A informação da distância total percorrida (a ida até o cliente e a volta) deve ser contabilizada e inserida no sistema no momento em que o atendimento é dado como encerrado
.
Campo Específico na Ordem de Serviço: O sistema precisará de um campo numérico dedicado aos KMs Percorridos dentro do formulário digital da OS. Esse recurso espelha o formulário físico atual da empresa, que já possui esse espaço específico posicionado junto à seção de "Valor da Mão de Obra"
.
Prestação de Contas para Fabricantes: O armazenamento exato dessa quilometragem é uma etapa fundamental do negócio. Nos casos de atendimentos em garantia (onde a empresa atua como credenciada), o setor administrativo precisa enviar a quilometragem total, juntamente com a OS finalizada e o valor da mão de obra, para receber o repasse correto do fabricante
.
Para a modelagem do software, isso significa que a entidade "Ordem de Serviço" deve conter obrigatoriamente um atributo de Km_Percorrido, que será preenchido pelo administrativo com base no repasse dos técnicos, permitindo assim o cálculo de custos ou a prestação de contas antes do fechamento final
.


Sincronização de Ordens de Serviço por Fabricante
(As respostas salvas são somente para visualização)
De acordo com os materiais, a empresa atua como credenciada de três fabricantes principais: Agratto, Gree e TCL
.
Atualmente, a responsável relata que cada fabricante possui um modelo diferente de Ordem de Serviço exigido para a prestação de contas
. Por exemplo, os documentos mostram um formulário de OS que é exclusivo da Agratto, o qual a administração considera o mais prático de preencher
.
Para que o novo sistema diferencie essas ordens de serviço, a modelagem precisaria adotar as seguintes estratégias:
Vinculação à Marca do Equipamento: Como o sistema manterá um inventário detalhado com a marca de cada máquina (Agratto, Gree, Midea, TCL, etc.)
, a Ordem de Serviço aberta para uma manutenção ou garantia estaria automaticamente vinculada à fabricante daquele equipamento
.
Templates Dinâmicos de OS: Como o áudio especifica que "cada uma tem um modelo diferente"
, o sistema idealmente teria templates (modelos visuais ou de campos) configuráveis. Assim, ao gerar uma OS para um equipamento da Agratto, o sistema exibiria o layout e os campos exclusivos que essa fabricante exige (como os checklists de instalação visíveis no formulário físico)
. Se o atendimento fosse para a Gree ou TCL, o sistema adaptaria a visualização e os campos obrigatórios para os padrões destas outras marcas.
Controle de Garantia e Repasse: O sistema também usaria essa diferenciação por fabricante para organizar o faturamento e o envio de dados, separando quais OSs finalizadas, com suas respectivas quilometragens e fotos, devem ser enviadas para a Agratto, para a Gree ou para a TCL para fins de reembolso e prestação de contas
.