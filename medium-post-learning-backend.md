## What twelve years of React didn't teach me about a for loop

I've been a frontend engineer for over a decade. React, TypeScript, the usual. I know my way around a component tree better than I know my own kitchen. And for a while now I've had this nagging feeling that I only understand half the picture. I ship the UI, someone else's API feeds it, and I've never really had to sit on the other side of that fence.

So a few weeks ago I decided to build one. A small Reading Tracker API in Python, using FastAPI — partly because I wanted an actual change of language, not just a new framework wearing the same JavaScript underneath. I paired with Claude the whole way through, but not in the "generate my code for me" sense. I wrote every endpoint myself. Claude scaffolded the concepts I hadn't seen before, then reviewed what I wrote, then we tested it for real with curl before moving on. If something was broken, I had to go back and fix it.

That last part turned out to be the whole point.

### The bugs told me more than the wins did

Here's a delete endpoint I wrote, more or less verbatim:

```python
book = session.get(Book, book_id)
if book is not None:
    session.delete(book)
    session.commit()

raise HTTPException(status_code=404, detail="Book not found")
```

Looks fine at a glance. It isn't. The 404 fires every single time, success or not, because I'd put it outside the `if` block instead of in an `else`. I've written this exact shape of bug in JavaScript too, just with a different word for it — an early return that runs before it should, or after it should, because I was thinking about the happy path and not about where control actually flows once the check fails.

Then there was this, in a query filter:

```python
Book.title.lower().contains(search.lower())
```

Total non-starter. `.lower()` doesn't exist on a SQLAlchemy column the way it does on a Python string — that column is a query-builder object, not a value, and it doesn't know what "lowercase" means until the database runs the query. I only found out because the server threw a 500 the second I actually tested it with curl, instead of just eyeballing the code and assuming it was fine. That's the bit I'd have skipped if I were doing this alone with a tutorial open in another tab.

And the quiet one, which I did twice: reaching for `session.remove()`, `session.refresh(session)`, calling `.model_dump()` on the wrong variable because two things in the function had similar-sounding names. Nothing exotic. Just tired-brain, wrong-object mistakes that only show up when someone actually reads your code line by line and asks "wait, which `book` is this."

### Why this felt different from just following a tutorial

I've tried the "watch a course, copy the code" route before. It never sticks the same way. What made this stick was closer to what I get from a good senior engineer during a real code review — someone who doesn't just say "this is wrong," but tells you why, and makes you go fix it yourself rather than pasting in the correct version. Claude did that consistently, catching the same category of mistake more than once and naming it as a pattern instead of a one-off ("this is the same ordering bug as before"), which is exactly the kind of feedback that eventually makes you stop making it.

By the end I had a proper little API: full CRUD, SQLite instead of an in-memory list, filtering, pagination, and a real pytest suite I wrote test by test with the same back and forth. Nothing about it is groundbreaking. But it's mine, in the sense that I understand every line of it and every mistake that got fixed along the way.

### If you're a frontend engineer who's curious

I don't think backend is some separate universe you need years to enter. A lot of it is the same discipline I already use every day — thinking about data shape, state, what happens when something's missing, testing before you trust it. The syntax is different. The instinct underneath mostly isn't.

If you've got a weekend and an idea for something small, build it the way I did: write the logic yourself, get it reviewed properly, and don't move to the next piece until the last one actually runs.
