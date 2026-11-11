# Submission

Fork URL: <!-- paste the URL of your fork here -->

## Files to commit

- [ ] `notes.md` with your commands (optional)

## Questions

Answer in your own words. Where a question asks for output, paste it in a code block.

### Q1. Paste the policy assignments you created (name, definition, scope, effect). Which built-in definitions did you choose and why built-in rather than custom? What is the difference between the effects `deny`, `audit` and `modify`?

**Your answer:**

<!-- replace this line with your answer -->

### Q2. Paste the error Azure gave when you tried to create a resource without the `owner` tag, and the one for a forbidden region. Which part of the message names the policy that blocked you? Where would an auditor read this later (Activity log)?

**Your answer:**

<!-- replace this line with your answer -->

### Q3. Why did the new policy not block you immediately? How long did it take, and what does that tell you about relying on a policy during a rollout? What is the difference between policy and RBAC (what you may *do* vs what is *allowed to exist*)?

**Your answer:**

<!-- replace this line with your answer -->

### Q4. Paste your budget (amount, period, thresholds). What does a budget do when it is exceeded: stop spending or only notify? What would you add to actually stop a runaway cost (an action group, automation, a policy on SKUs)?

**Your answer:**

<!-- replace this line with your answer -->

### Q5. Paste the failed delete under the `CanNotDelete` lock. Who can remove a lock, and how does it differ from RBAC? Why must teardown remove the lock first?

**Your answer:**

<!-- replace this line with your answer -->

### Q6. Policy at the scope of a resource group, a subscription and a management group: what is inherited, what can be excluded, and which scope would you assign a company-wide rule to?

**Your answer:**

<!-- replace this line with your answer -->

### Q7. Azure quota and policy can both say "no". Explain how you tell a quota error (`QuotaExceeded`) from a policy error (`RequestDisallowedByPolicy`), and who you ask for help in each case.

**Your answer:**

<!-- replace this line with your answer -->

### Q8. Paste the output of `./verify.sh`. It must end with **ALL CHECKS PASSED**.

**Your answer:**

<!-- replace this line with your answer -->

### Q9. **Tear down.** Paste the output of `./verify-teardown.sh`. It must end with **TEARDOWN VERIFIED**.

**Your answer:**

<!-- replace this line with your answer -->
