---
name: better-prompt
description: Rewrite a prompt into a deeper version of the same task, the way a top professional would approach it. Use only when explicitly invoked with /better-prompt.
disable-model-invocation: true
triggers: [user, model]
---

I want a deeper version of this task, not a bigger one. Before rewriting it: (1) say what a top professional in this field would do here that I'm not asking for; (2) name the rawest material they would start from instead of what has already been digested for me; (3) name the specific methods and tools they would use; (4) say what, other than you or me, would show the result is right. Then rewrite my prompt to ask for exactly that.
