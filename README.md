# talks4all.github.io

Site das palestras sobre inteligência artificial de Diego Kreutz, em português, inglês e espanhol. Publicado pelo GitHub Pages em https://talks4all.github.io.

## Como funciona

Todo o conteúdo fica em `content/`, em JSON. O `build.py` lê esses arquivos e escreve HTML estático na raiz do repositório, uma árvore de páginas por idioma. Não há dependência externa: basta Python 3.9 ou mais novo.

```
content/site.json              textos do site (nome, bio, rótulos de interface) nos três idiomas
content/talks/<slug>.json      uma palestra, com os três idiomas dentro
assets/css/site.css            folha de estilo única
assets/js/lang.js              guarda o idioma escolhido para a próxima visita
files/                         slides para download (PDF, PPTX)
build.py                       gerador
```

Páginas geradas (não edite à mão, elas são sobrescritas a cada build):

```
index.html                     raiz: detecta o idioma do navegador e redireciona
pt/ en/ es/                    página inicial de cada idioma
pt/<slug>/ en/<slug>/ es/<slug>/   página de cada palestra
404.html  sitemap.xml  robots.txt  .nojekyll
```

## Gerar o site

```sh
python3 build.py
```

O comando apaga e recria as pastas `pt/`, `en/` e `es/`. Depois é só commitar o resultado: o GitHub Pages publica a raiz do branch principal.

## Adicionar uma palestra

1. Crie `content/talks/<slug>.json` copiando a estrutura de uma palestra existente. O `slug` vira o endereço da página, então use apenas letras minúsculas, números e hífens.
2. Preencha os três idiomas em `i18n`. Os campos `host` e `numbers` são opcionais; os demais aparecem sempre.
3. Preencha `date_iso` no formato `AAAA-MM-DD`, ou `AAAA-MM` quando só o mês for conhecido. Ele define a data mostrada na listagem e a ordem, que é sempre da palestra mais recente para a mais antiga. Ajuste também `status`, que aceita `upcoming` ou `past`.
4. Coloque os slides em `files/` e aponte o nome do arquivo em `downloads`. O tamanho mostrado no site é lido do arquivo durante o build.
5. Rode `python3 build.py`.

## Adicionar um idioma

Acrescente o código em `languages` e `language_names` no `content/site.json`, traduza o bloco correspondente em `i18n` e repita o mesmo bloco dentro de cada palestra. O gerador cria a árvore nova sozinho.

## Licença

Código sob a licença do arquivo `LICENSE`. O conteúdo das palestras é de Diego Kreutz.
