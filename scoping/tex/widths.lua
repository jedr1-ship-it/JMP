local function cell_len(cell) return #pandoc.utils.stringify(cell.contents) end
local function is_wide(b) return b.t == 'Table' and #b.colspecs >= 6 end
function Table(tbl)
  local ncol = #tbl.colspecs
  if ncol < 3 then return nil end
  local maxlen = {}
  for i=1,ncol do maxlen[i] = 3 end
  local maxword = {}
  for i=1,ncol do maxword[i] = 3 end
  local function scan(rows)
    for _,row in ipairs(rows) do
      for i,cell in ipairs(row.cells) do
        local l = math.min(cell_len(cell), 90)
        if l > maxlen[i] then maxlen[i] = l end
        for w in pandoc.utils.stringify(cell.contents):gmatch('[^%s/]+') do if #w > maxword[i] then maxword[i] = #w end end
      end
    end
  end
  scan(tbl.head.rows)
  for _,body in ipairs(tbl.bodies) do scan(body.body) end
  local total = 0
  for i=1,ncol do maxlen[i] = math.max(maxlen[i]^0.8, maxword[i]*0.85); total = total + maxlen[i] end
  for i=1,ncol do tbl.colspecs[i] = {tbl.colspecs[i][1], 0.97 * maxlen[i] / total} end
  return tbl
end
function Pandoc(doc)
  local out = {}
  local blocks = doc.blocks
  local n = #blocks
  local i = 1
  local open = false
  local function push(b) table.insert(out, b) end
  while i <= n do
    local b = blocks[i]
    local nxt = blocks[i+1]
    local wide_here = is_wide(b) or (b.t == 'Header' and nxt and is_wide(nxt))
    if wide_here then
      if not open then push(pandoc.RawBlock('latex','\\begin{landscape}')); open = true end
      push(b)
      if b.t == 'Header' then push(nxt); i = i + 1 end
    else
      -- allow short paragraphs between wide tables to stay in landscape
      local keep = open and b.t == 'Para' and nxt and (is_wide(nxt) or (nxt.t=='Header' and blocks[i+2] and is_wide(blocks[i+2])))
      if open and not keep then push(pandoc.RawBlock('latex','\\end{landscape}')); open = false end
      push(b)
    end
    i = i + 1
  end
  if open then push(pandoc.RawBlock('latex','\\end{landscape}')) end
  doc.blocks = out
  return doc
end

function Str(el)
  if #el.text > 10 and el.text:find('/', 1, true) then
    local parts = {}
    local first = true
    for piece in (el.text .. '/'):gmatch('([^/]*)/') do
      if not first then table.insert(parts, pandoc.RawInline('latex', '/\\allowbreak{}')) end
      if piece ~= '' then table.insert(parts, pandoc.Str(piece)) end
      first = false
    end
    return parts
  end
end
