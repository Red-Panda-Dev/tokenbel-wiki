# {{ .Title }}

{{ with .Description }}
{{ . }}

{{ end }}{{ with .Sections.ByWeight }}

## Разделы

{{ range . }}- [{{ .Title }}]({{ .Permalink }}){{ with .Description }} — {{ . }}{{ end }}
{{ end }}
{{ end }}{{ with .RegularPages.ByLastmod.Reverse }}

## Материалы

{{ range . }}- [{{ .Title }}]({{ .Permalink }}) — обновлено {{ .Lastmod.Format "2006-01-02" }}
{{ end }}
{{ end }}
