import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'
import katexPlugin from 'markdown-it-katex-gpt'

export interface TocItem {
  id: string
  text: string
  level: number
}

function createMd() {
  const md = new MarkdownIt({
    html: true,
    linkify: true,
    typographer: true,
    highlight(str, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang }).value}</code></pre>`
        } catch {}
      }
      return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
    },
  })

  const plugin = typeof katexPlugin === 'function'
    ? katexPlugin
    : (katexPlugin as any).default

  if (typeof plugin === 'function') {
    md.use(plugin)
  }

  return md
}

export function useMarkdown(source: string) {
  const md = createMd()
  const toc: TocItem[] = []
  const slugCounter: Record<string, number> = {}

  function slugify(text: string): string {
    const base = text
      .toLowerCase()
      .replace(/[^\w\u4e00-\u9fff]+/g, '-')
      .replace(/^-|-$/g, '')
      || 'heading'

    slugCounter[base] = (slugCounter[base] || 0) + 1
    return slugCounter[base] > 1 ? `${base}-${slugCounter[base]}` : base
  }

  const originalOpen = md.renderer.rules.heading_open
  md.renderer.rules.heading_open = (tokens, idx, options, env, self) => {
    const token = tokens[idx]
    const level = Number(token.tag.slice(1))
    if (level >= 2 && level <= 4) {
      const inline = tokens[idx + 1]
      const text = inline?.children
        ?.filter(t => t.type === 'text' || t.type === 'code_inline')
        .map(t => t.content)
        .join('') ?? ''
      const id = slugify(text)
      toc.push({ id, text, level })
      token.attrSet('id', id)
    }
    return originalOpen
      ? originalOpen(tokens, idx, options, env, self)
      : self.renderToken(tokens, idx, options)
  }

  const html = md.render(source)

  return { html, toc }
}
