export default defineEventHandler(async (event) => {
  const baseUrl = 'https://qingkong.dev'
  const apiBase = 'http://127.0.0.1:8000/qingkong'

  const staticPages = ['', '/archives', '/categories', '/tags', '/about', '/search']

  let postUrls: string[] = []
  let categoryUrls: string[] = []
  let tagUrls: string[] = []

  try {
    const postsRes = await $fetch<{ items: { slug: string }[] }>(`${apiBase}/posts`, {
      params: { pageSize: 1000, status: 'published' },
    })
    postUrls = postsRes.items.map(p => `/post/${p.slug}`)
  } catch {}

  try {
    const categories = await $fetch<{ slug: string }[]>(`${apiBase}/categories`)
    const flatSlugs = (list: any[]): string[] => {
      const result: string[] = []
      for (const c of list) {
        result.push(c.slug)
        if (c.children?.length) result.push(...flatSlugs(c.children))
      }
      return result
    }
    categoryUrls = flatSlugs(categories).map(s => `/categories/${s}`)
  } catch {}

  try {
    const tags = await $fetch<{ slug: string }[]>(`${apiBase}/tags`)
    tagUrls = tags.map(t => `/tags/${t.slug}`)
  } catch {}

  const allUrls = [...staticPages, ...postUrls, ...categoryUrls, ...tagUrls]
  const today = new Date().toISOString().split('T')[0]

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${allUrls.map(url => `  <url>
    <loc>${baseUrl}${url}</loc>
    <lastmod>${today}</lastmod>
  </url>`).join('\n')}
</urlset>`

  setResponseHeader(event, 'content-type', 'application/xml; charset=utf-8')
  return xml
})
