# {{ .Title }}

{{ with .Description }}
{{ . }}

{{ end }}{{ with .RawContent }}
{{ . }}

{{ end }}{{ with site.Sections.ByWeight }}

## Разделы

{{ range . }}- [{{ .Title }}]({{ .Permalink }}){{ with .Description }} — {{ . }}{{ end }}
{{ end }}
{{ end }}
