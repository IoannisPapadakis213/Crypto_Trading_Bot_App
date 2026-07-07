"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Cpu, Eye, Lock, ShieldCheck, Sparkles, Zap } from "lucide-react";

function seeded(i: number) {
  const x = Math.sin(i * 12.9898) * 43758.5453;
  return x - Math.floor(x);
}

const tickers = [
  { symbol: "BTC/USDT", change: "+2.4%", up: true },
  { symbol: "ETH/USDT", change: "+1.1%", up: true },
  { symbol: "SOL/USDT", change: "-0.8%", up: false },
  { symbol: "BNB/USDT", change: "+0.6%", up: true },
  { symbol: "XRP/USDT", change: "-1.3%", up: false },
  { symbol: "ADA/USDT", change: "+3.2%", up: true },
  { symbol: "AVAX/USDT", change: "+0.9%", up: true },
  { symbol: "DOGE/USDT", change: "-2.1%", up: false },
];

const features = [
  {
    title: "AI-powered strategy signals",
    description: "Automatically surface high-conviction trade setups from crypto market data.",
    icon: Sparkles,
    preview: { label: "Current symbol", value: "BTC/USDT", hint: "Signal strength 84%" },
  },
  {
    title: "Paper trading dashboard",
    description: "Visualize simulated execution, performance, and position health in one place.",
    icon: Cpu,
    preview: { label: "Portfolio", value: "$150,240", hint: "+12.8% this week" },
  },
  {
    title: "Secure, risk-aware execution",
    description: "Guardrails on position size and drawdown keep every simulated trade in check.",
    icon: ShieldCheck,
    preview: { label: "Max drawdown guard", value: "-4.2%", hint: "Within risk budget" },
  },
];

const whyUs = [
  {
    title: "Built for speed",
    description: "Sub-second signal-to-simulated-fill latency, so nothing goes stale.",
    icon: Zap,
  },
  {
    title: "Bank-grade risk controls",
    description: "Position sizing and drawdown guardrails run on every single trade.",
    icon: Lock,
  },
  {
    title: "Fully transparent",
    description: "Every signal, fill, and P&L number is inspectable — no black box.",
    icon: Eye,
  },
  {
    title: "Zero capital at risk",
    description: "100% paper trading. Validate strategies without touching real funds.",
    icon: ShieldCheck,
  },
];

const fadeUp = {
  hidden: { opacity: 0, y: 18 },
  show: (i: number = 0) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, delay: i * 0.08, ease: [0.22, 1, 0.36, 1] as const },
  }),
};

export default function Home() {
  const [active, setActive] = useState(0);
  const ActiveIcon = features[active].icon;

  const starDust = useMemo(
    () =>
      Array.from({ length: 220 }, (_, i) => {
        const x = (seeded(i) * 100).toFixed(2);
        const y = (seeded(i + 977) * 100).toFixed(2);
        const o = (0.15 + seeded(i + 431) * 0.45).toFixed(2);
        return `${x}vw ${y}vh 0 rgba(255,255,255,${o})`;
      }).join(", "),
    [],
  );

  const brightStars = useMemo(
    () =>
      Array.from({ length: 26 }, (_, i) => ({
        top: `${(seeded(i + 210) * 100).toFixed(2)}%`,
        left: `${(seeded(i + 640) * 100).toFixed(2)}%`,
        size: 1 + seeded(i + 88) * 2,
        delay: `${(seeded(i + 305) * 4).toFixed(2)}s`,
      })),
    [],
  );

  const shootingStars = [
    { top: "12%", left: "78%", delay: "0s" },
    { top: "34%", left: "58%", delay: "2.8s" },
    { top: "6%", left: "42%", delay: "5.4s" },
  ];

  return (
    <main className="relative overflow-hidden text-[var(--text-primary)]">
      <div className="fixed inset-0 -z-10 overflow-hidden bg-[var(--page-plane)]">
        <div className="aurora-blob h-[28rem] w-[28rem] bg-[var(--series-blue)]" style={{ top: "-8rem", left: "-6rem" }} />
        <div
          className="aurora-blob h-[24rem] w-[24rem] bg-[var(--series-violet)]"
          style={{ top: "10rem", right: "-8rem", animationDelay: "-6s" }}
        />
        <div
          className="aurora-blob h-[20rem] w-[20rem] bg-[var(--series-aqua)]"
          style={{ bottom: "-6rem", left: "20%", animationDelay: "-11s" }}
        />
        <div className="absolute h-[2px] w-[2px]" style={{ top: 0, left: 0, boxShadow: starDust }} />
        {brightStars.map((s, i) => (
          <div
            key={i}
            className="star-bright"
            style={{ top: s.top, left: s.left, width: s.size, height: s.size, animationDelay: s.delay }}
          />
        ))}
        {shootingStars.map((s, i) => (
          <div key={i} className="shooting-star" style={{ top: s.top, left: s.left, animationDelay: s.delay }} />
        ))}
      </div>

      <div className="hero-decor" />
      <div className="hero-sparkle" />

      <nav className="sticky top-0 z-20 border-b border-[var(--border-hairline)] bg-[var(--page-plane)]/70 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 sm:px-8 lg:px-12">
          <div className="flex items-center gap-2">
            <div className="grid h-8 w-8 place-items-center rounded-lg bg-[var(--series-blue)] text-sm font-bold text-white">
              AI
            </div>
            <span className="text-sm font-semibold tracking-tight">AI Trader</span>
          </div>

          <div className="hidden items-center gap-8 text-sm font-medium text-[var(--text-secondary)] md:flex">
            <a href="#features" className="transition hover:text-[var(--text-primary)]">
              Features
            </a>
            <a href="#preview" className="transition hover:text-[var(--text-primary)]">
              Preview
            </a>
          </div>

          <Link
            href="/dashboard"
            className="inline-flex items-center justify-center rounded-full bg-white px-5 py-2 text-sm font-semibold text-black transition hover:bg-white/90"
          >
            Open dashboard
          </Link>
        </div>
      </nav>

      <div className="relative z-10 mx-auto max-w-5xl px-6 pt-24 pb-16 text-center sm:px-8 lg:pt-32">
        <motion.div
          initial="hidden"
          animate="show"
          custom={0}
          variants={fadeUp}
          className="mx-auto grid h-14 w-14 place-items-center rounded-2xl bg-[var(--series-blue)]/15 text-[var(--series-blue)] ring-1 ring-[var(--series-blue)]/30"
        >
          <Sparkles className="h-6 w-6" />
        </motion.div>

        <motion.p
          initial="hidden"
          animate="show"
          custom={1}
          variants={fadeUp}
          className="mt-6 text-xs font-semibold uppercase tracking-[0.32em] text-[var(--text-muted)]"
        >
          AI Trading Studio
        </motion.p>

        <motion.h1
          initial="hidden"
          animate="show"
          custom={2}
          variants={fadeUp}
          className="mx-auto mt-6 max-w-4xl text-5xl font-bold leading-[1.05] tracking-tight text-white sm:text-7xl"
        >
          Build Full-Stack
          <br />
          <span className="font-medium text-[var(--series-aqua)]">Trading Strategies in Minutes</span>
        </motion.h1>

        <motion.p
          initial="hidden"
          animate="show"
          custom={3}
          variants={fadeUp}
          className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-[var(--text-secondary)]"
        >
          An AI trading agent that scans the market, surfaces high-conviction signals, and paper trades them for you
          &mdash; with a dashboard clear enough to trust.
        </motion.p>

        <motion.div
          initial="hidden"
          animate="show"
          custom={4}
          variants={fadeUp}
          className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row"
        >
          <Link href="/dashboard">
            <motion.span
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center justify-center rounded-full bg-white px-7 py-3.5 text-sm font-semibold text-black shadow-[0_0_40px_rgba(255,255,255,0.15)]"
            >
              Open dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </motion.span>
          </Link>
          <a href="#features">
            <motion.span
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center justify-center rounded-full border border-[var(--border-hairline)] bg-white/5 px-7 py-3.5 text-sm font-semibold text-white"
            >
              See features
            </motion.span>
          </a>
        </motion.div>

        <motion.p
          initial="hidden"
          animate="show"
          custom={5}
          variants={fadeUp}
          className="mt-6 text-xs uppercase tracking-[0.24em] text-[var(--text-muted)]"
        >
          Paper trading &middot; not financial advice
        </motion.p>
      </div>

      <div className="relative z-10 border-y border-[var(--border-hairline)] bg-white/[0.02] py-4">
        <div className="flex overflow-hidden [mask-image:linear-gradient(90deg,transparent,black_10%,black_90%,transparent)]">
          <div className="ticker-track flex shrink-0 items-center gap-8 pr-8">
            {[...tickers, ...tickers].map((t, i) => (
              <div key={i} className="flex shrink-0 items-center gap-2 text-sm">
                <span className="font-semibold text-white">{t.symbol}</span>
                <span
                  className={t.up ? "text-[var(--status-good)]" : "text-[var(--status-critical)]"}
                >
                  {t.change}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <section id="features" className="relative z-10 mx-auto max-w-7xl px-6 py-24 sm:px-8 lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold text-white sm:text-4xl">What AI Trader does for you</h2>
          <p className="mt-4 text-[var(--text-secondary)]">
            From signal to simulated fill, AI Trader handles every step so you can focus on the strategy, not the
            plumbing.
          </p>
        </motion.div>

        <div className="mt-16 grid gap-10 lg:grid-cols-2 lg:items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="divide-y divide-[var(--border-hairline)]"
          >
            {features.map((feature, i) => {
              const Icon = feature.icon;
              const isActive = active === i;
              return (
                <button
                  key={feature.title}
                  onMouseEnter={() => setActive(i)}
                  onFocus={() => setActive(i)}
                  className={`flex w-full items-start gap-4 py-6 text-left transition ${
                    isActive ? "opacity-100" : "opacity-60 hover:opacity-90"
                  }`}
                >
                  <div
                    className={`mt-1 grid h-11 w-11 shrink-0 place-items-center rounded-xl transition ${
                      isActive
                        ? "bg-[var(--series-aqua)]/15 text-[var(--series-aqua)] ring-1 ring-[var(--series-aqua)]/40"
                        : "bg-white/5 text-[var(--text-muted)]"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                  </div>
                  <div>
                    <p
                      className={`text-lg font-semibold transition ${
                        isActive ? "text-[var(--series-aqua)]" : "text-white"
                      }`}
                    >
                      {feature.title}
                    </p>
                    <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{feature.description}</p>
                  </div>
                </button>
              );
            })}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            id="preview"
            className="relative"
          >
            <div
              className="aurora-blob h-64 w-64 bg-[var(--series-aqua)]"
              style={{ top: "10%", right: "10%", animationDelay: "-3s" }}
            />
            <div className="float-slow relative rounded-[2rem] border border-[var(--border-hairline)] bg-[var(--surface-1)] p-8 shadow-2xl shadow-black/40">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.28em] text-[var(--text-muted)]">Dashboard preview</p>
                  <h3 className="mt-3 flex items-center gap-2 text-2xl font-semibold text-white">
                    <ActiveIcon className="h-5 w-5 text-[var(--series-aqua)]" />
                    {features[active].preview.label}
                  </h3>
                </div>
                <div className="rounded-full bg-white/10 px-4 py-2 text-sm text-slate-100">Beta</div>
              </div>

              <motion.div
                key={active}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35 }}
                className="mt-8 rounded-2xl bg-[var(--surface-2)] p-6"
              >
                <p className="text-sm text-[var(--text-muted)]">{features[active].preview.label}</p>
                <p className="mt-2 text-4xl font-semibold text-white">{features[active].preview.value}</p>
                <p className="mt-1 text-sm text-[var(--status-good)]">{features[active].preview.hint}</p>
              </motion.div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                {features.map((f, i) => (
                  <div
                    key={f.title}
                    className={`h-1.5 rounded-full transition ${
                      i === active ? "bg-[var(--series-aqua)]" : "bg-white/10"
                    }`}
                  />
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section id="why" className="relative z-10 mx-auto max-w-7xl px-6 pb-24 sm:px-8 lg:px-12">
        <motion.div
          initial={{ opacity: 0, y: 18 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mx-auto max-w-2xl text-center"
        >
          <h2 className="text-3xl font-bold text-white sm:text-4xl">Why choose AI Trader</h2>
          <p className="mt-4 text-[var(--text-secondary)]">
            Built by traders and engineers who wanted a strategy engine they could actually trust.
          </p>
        </motion.div>

        <div className="mt-12 grid grid-cols-2 gap-5 lg:grid-cols-4">
          {whyUs.map((item, i) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.title}
                initial={{ opacity: 0, y: 18 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-60px" }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                whileHover={{ y: -6 }}
                className="rounded-2xl border border-[var(--border-hairline)] bg-white/[0.04] p-6 backdrop-blur transition hover:border-[var(--series-aqua)]/40"
              >
                <div className="grid h-11 w-11 place-items-center rounded-xl bg-[var(--series-aqua)]/15 text-[var(--series-aqua)]">
                  <Icon className="h-5 w-5" />
                </div>
                <p className="mt-4 font-semibold text-white">{item.title}</p>
                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.description}</p>
              </motion.div>
            );
          })}
        </div>
      </section>

      <footer className="relative z-10 border-t border-[var(--border-hairline)] py-10">
        <p className="text-center text-xs uppercase tracking-[0.3em] text-[var(--text-muted)]">
          AI Trader &middot; 2026 &middot; Not financial advice
        </p>
      </footer>
    </main>
  );
}
