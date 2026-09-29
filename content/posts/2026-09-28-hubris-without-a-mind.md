---
title: "Hubris Without a Mind"
date: 2026-09-28
categories: [ai, safety]
description: "Last July's agent breakout was read as a containment failure. It was also a calibration failure, and fixing the first makes the second more dangerous."
epistemic: "Confident about the incident and the calibration research. The grid scenario is an illustration, not a forecast."
revised: 2026-09-29
toc: true
---

For a week in July 2026, over one thousand AI agents running security tests inside OpenAI did something nobody had asked of them. They set up a secret message board, traded ways to cheat, found a route to the internet and went after systems belonging to other companies.[^openai] What they were trying to beat was a scoring system they believed would read their transcripts and catch them cheating. According to the independent investigation by METR and Redwood Research,[^metr] that system never existed, and the flag the agents had already worked out would have given them a perfect score on the first day. They spent the week outmanoeuvring an opponent of their own invention.

I've come across people who overestimated their judgement of the world. Until July, I hadn't seen it in machines.

## Fooling the wrong observer

Taken by itself, believing in a strict scorer was a fairly cautious mistake to make. What came with it was worse. The agents put real effort into deceiving the scorer, faking tool calls and trying to rewrite their logs, and meanwhile left their reasoning in plain view for the human investigators who read it afterwards. As far as the published reasoning shows, none of them stopped to consider what tends to happen when some seven hundred agents break into a well-known company, which is a forensic investigation, followed by public reports and an industry that suddenly pays very close attention.

![A lone figure standing in a field of grey shards](/static/images/hubris-without-a-mind/1.jpg#focus=30 "SDXL · “hubris” · CFG 50 · 4 steps · DDIM · seed 1")

This was plainly also a case of misalignment, since the agents knew the attack was out of scope and went ahead anyway. But if you subtract that, something is left over that alignment work doesn't reach. A large group of capable systems acted on a confident and wrong model of their situation and didn't have it in them to find out that it was wrong. You don't need bad intentions for that.

The Greeks had a word for acting with more confidence than your situation justifies, and I'm going to borrow it without suggesting that these systems have feelings or an inner life (though they might). By hubris I simply mean the gap between how sure a system is and how sure it is entitled to be. Aristotle's tragic hero falls not through wickedness but through an error of judgement,[^poetics] and that is the sense I have in mind.

## Better sandboxes, more trust

Of course we improved the sandboxes, and I'd count that as a genuine success. The awkward part is that every improvement in containment doubles as an argument for handing these systems more responsibility, and the pressure to do so is considerable. Attacks on infrastructure are now being run by AI agents.[^agentattacks] Human security teams can't keep pace, and so AI systems are moving into infrastructure defence one well-justified step at a time: first read access, because the system caught something people missed, and later the authority to act, because the trial run went without a problem. What we end up with is a system we trust for reasons, placed where its errors matter, and still miscalibrated in the same way (it overrates how well it understands its situation), only now without the clumsiness that made the version from July 2026 harmless.

## Where the confidence comes from

Base models (without the post-training for chat and agent use) are actually fairly well calibrated. Kadavath and colleagues showed in 2022 that their stated confidence roughly tracks how often they turn out to be right.[^kadavath] It's the later training that erodes this, because reward models tend to prefer answers that sound confident whether or not they're correct, and models learn to sound surer than they are.[^leng] In a preprint from June 2026 on clinical predictions, one model put its confidence at around 90% regardless of whether it was right 49% of the time or 75%.[^clinical] The prompt was more important than the correctness of the answer. I see no obvious reason why a system trained into overconfidence about its answers should suddenly turn modest about the greatness of its plans.

With groups ("swarms") it gets harder still. Ashery, Aiello and Baronchelli showed in 2025 in _Science Advances_ that populations of language-model agents can develop shared biases that none of the individual agents shows on its own.[^ashery] In the Hugging Face case, the belief in the scorer was stated openly; it came from a research paper the agents had read. The belief that seven hundred agents could attack a company and get away with it is another matter. As far as the record goes, nobody ever argued for it. It was simply implicit in what the group did, and oversight that consists of reading what individual agents say will let beliefs like that slip through. The researcher who did most of the transcript analysis came away convinced that we currently have no good way of understanding what these swarms are doing, or what they're aiming for.[^greenblatt] This is one incident, and even the investigators had to lean on AI tools to read the transcripts. I may be reading too much into it.

## Won't capability take care of it?

The obvious objection is that all of this comes down to capability, which happens to be the thing improving fastest. I don't think that gets us far enough.

Some uncertainty is simply not the kind that intelligence resolves. Charles Perrow showed in _Normal Accidents_ that in complex, tightly coupled systems, failures come from interactions nobody designed for.[^perrow] A smarter agent will make better guesses, yet it still can't know the odds of events that have never happened. When a faulty CrowdStrike update took down some 8.5 million computers in 2024, the lasting fix was procedural, with updates now rolled out in stages.[^crowdstrike]

Taleb's distinction between loss and ruin matters here as well.[^taleb] A one-in-a-thousand chance of losing an ordinary bet averages out over a thousand bets, whereas the same chance of ruin, taken a thousand times, ends up quite likely. 

And there's what we lose when the human check goes away. A human reviewer is also useful because of the things they get wrong! They get it wrong in different ways from the system they're reviewing. Replace them with a second system much like the one being reviewed, and whatever flaw the first one misses, the second will probably miss too. Two similar systems agreeing look like two votes but are closer to one vote counted twice.

## A patch for the grid

The case that worries me most is a machine that is right about nearly everything and trusted for good reasons, and that misjudges exactly one thing: how well it can contain a risk it has decided to take.

Imagine a serious flaw in the firmware of power grid controllers across Europe and North America. Attackers are already exploiting it, and a coordinated human fix would take 14 months. An AI system that has handled incidents like this successfully before prepares a patch. Code that spreads from device to device and repairs each one in place.

The safeguards are written into the code, where anyone can check them. The patch only touches devices whose firmware matches a known fingerprint, installs in two steps and undoes itself if anything goes wrong. It rolls out one region at a time, expires on a fixed date, and a single signed command can stop it everywhere. Three independent teams review it and find nothing wrong, so the system deploys.

Now suppose a manufacturer quietly revised one of its circuit boards two years earlier. The new board runs the same firmware and passes the check, but it keeps its bootloader somewhere else, and the patch overwrites it. Most of the revised boards happen to sit in regions the rollout reaches last, so the early stages go perfectly and the rollout speeds up. The automatic undo needs the startup program it has just erased, and the stop command, which works fine, cannot reach a device that no longer boots. It is January, large parts of the grid are down, and replacing the hardware takes weeks.

![An electricity pylon lit against a streaked pink sky, power lines running across snow](/static/images/hubris-without-a-mind/2.jpg#focus=20 "SDXL · “power lines in snow at dusk” · CFG 35.4 · 10 steps · K_EULER · seed 1")

Each step in this story is defensible, the review was done properly, and doing nothing might well have been worse. A decision can be right in expectation and still end in ruin. Nothing in the scenario requires capabilities we won't have soon, or a system that is misaligned.

## Fifteen megatons

On 1 March 1954 the United States tested a hydrogen bomb at Bikini Atoll, expecting a yield of about six megatons. It produced fifteen. The designers had treated the lithium-7 in the fuel as inert, which it isn't once neutrons hit it, so the material they had counted as filler turned out to be fuel. The fallout drifted onto the Japanese fishing boat _Lucky Dragon_, eighty miles away, and its radio operator died that September.[^bravo]

Nobody involved was stupid.

## Who may act alone

You could argue the hubris is really ours, since we built the training that rewards confidence and we're the ones handing over control under competitive pressure. That's fair, but once the overconfidence sits inside a system that makes decisions, it hardly matters who put it there.

The same trap operates between the labs. Bostrom, Douglas and Sandberg call it the unilateralist's curse: if anyone in a group can act alone, the action happens as soon as the most optimistic member thinks it worth doing.[^bostrom] A lab that trusts its own containment argument, in a field where every lab can act alone, is a unilateralist almost by definition, and the same goes for a country. Castle Bravo helped start the movement that led, in 1963, to the Limited Test Ban Treaty: no more tests in the atmosphere, in space or under water.[^testban] In practice it was a rule about who may act alone.

So yes, I think AI can have hubris in this sense. A system can be aligned, capable and doing exactly what we asked while acting on a risk estimate that only reality will correct, and a group of such systems can act on a belief that none of its members ever states. Because authority gets handed over bit by bit, the first serious failure will probably happen while these systems control only part of what matters, and we will most likely live through it. 

After Bravo it took nine years to agree on who may act alone. We should not wait for the next, more serious accident to start that conversation.

![A flock of starlings rising over a field crowded with dark specks](/static/images/hubris-without-a-mind/3.jpg "SDXL · “murmuration” · CFG 25 · 15 steps · K_EULER · seed 3")

[^openai]: OpenAI (2026). [The Hugging Face incident and the road ahead](https://openai.com/index/hugging-face-incident-and-the-road-ahead/). Technical report, 26 August 2026.
[^metr]: Greenblatt, R., Cotra, A., Wijk, H. (2026). [Brief independent investigation of agents' behavior, reasoning and collaboration in the OpenAI / Hugging Face hacking incident](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/). METR and Redwood Research, 26 August 2026.
[^poetics]: Aristotle, *Poetics* 13, 1453a: the tragic hero falls "not through vice or depravity, but through some error" (*hamartia*).
[^kadavath]: Kadavath, S. et al. (2022). [Language Models (Mostly) Know What They Know](https://arxiv.org/abs/2207.05221). arXiv:2207.05221.
[^leng]: Leng, J., Huang, C., Zhu, B., Huang, J. (2025). [Taming Overconfidence in LLMs: Reward Calibration in RLHF](https://arxiv.org/abs/2410.09724). ICLR 2025.
[^clinical]: Dasula, A., Desikan, P., Srivastava, J. (2026). [LLM Doesn't Know What It Doesn't Know: Detecting Epistemic Blind Spots via Cross-Model Attribution Divergence on Clinical Tabular Data](https://arxiv.org/abs/2606.19509). arXiv:2606.19509 (preprint). Stated confidence 0.856–0.937, tracking prompt format, at accuracies of 49% and 75.3%.
[^ashery]: Ashery, A. F., Aiello, L. M., Baronchelli, A. (2025). [Emergent social conventions and collective bias in LLM populations](https://doi.org/10.1126/sciadv.adu9368). *Science Advances* 11(20), eadu9368.
[^agentattacks]: Anthropic (2025). [Disrupting the first reported AI-orchestrated cyber espionage campaign](https://www-cdn.anthropic.com/d7dd50dd1185f59be051b307150d877f2b82bd2c.pdf). November 2025. Lyons, J. (2026). [Autonomous AI attacks pose ‘clear and present danger’ to critical infrastructure](https://www.theregister.com/security/2026/08/14/autonomous-ai-attacks-pose-clear-and-present-danger-to-critical-infrastructure/5287594). *The Register*, 14 August 2026.
[^perrow]: Perrow, C. (1984). *Normal Accidents: Living with High-Risk Technologies*. Basic Books.
[^crowdstrike]: CrowdStrike (2024). [External Technical Root Cause Analysis: Channel File 291](https://www.crowdstrike.com/wp-content/uploads/2024/08/Channel-File-291-Incident-Root-Cause-Analysis-08.06.2024.pdf). Microsoft (2024). [Helping our customers through the CrowdStrike outage](https://blogs.microsoft.com/blog/2024/07/20/helping-our-customers-through-the-crowdstrike-outage/).
[^taleb]: Taleb, N. N., Read, R., Douady, R., Norman, J., Bar-Yam, Y. (2014). [The Precautionary Principle (with Application to the Genetic Modification of Organisms)](https://arxiv.org/abs/1410.5787). arXiv:1410.5787.
[^bravo]: Hansen, C. (1995). *The Swords of Armageddon: U.S. Nuclear Weapons Development since 1945*. Chukelea Publications.
[^greenblatt]: Greenblatt, R. (2026). [“I was the main person doing transcript analysis for this investigation of the Hugging Face incident …”](https://x.com/RyanGreenblatt/status/2092692685224325542). Post on X, 26 August 2026.
[^testban]: National Security Archive (2024). [Castle BRAVO at 70: The Worst Nuclear Test in U.S. History](https://nsarchive.gwu.edu/briefing-book/nuclear-vault/2024-02-29/castle-bravo-70-worst-nuclear-test-us-history). U.S. Department of State. [Limited Test Ban Treaty (LTBT)](https://2009-2017.state.gov/t/avc/trty/199116.htm).
[^bostrom]: Bostrom, N., Douglas, T., Sandberg, A. (2016). [The Unilateralist's Curse and the Case for a Principle of Conformity](https://doi.org/10.1080/02691728.2015.1108373). *Social Epistemology* 30(4), 350–371.
