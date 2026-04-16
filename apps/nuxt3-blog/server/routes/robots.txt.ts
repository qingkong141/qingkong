export default defineEventHandler((event) => {
  const content = `User-agent: *
Allow: /
Disallow: /search

Sitemap: https://qingkong.dev/sitemap.xml`

  setResponseHeader(event, 'content-type', 'text/plain; charset=utf-8')
  return content
})
