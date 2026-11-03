import { type ChangeEvent, useMemo, useState } from 'react'
import { BrowserRouter, NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'

type PredictionEstimate = {
  label: string
  confidence: number
  confidenceLabel: string
  heatmap: string
}

type HistoryItem = {
  id: string
  label: string
  confidence: number
  date: string
  status: 'Reviewed' | 'Pending' | 'Flagged'
}

const modelMetrics = [
  { label: 'Accuracy', value: '96.8%', trend: '+4.2%' },
  { label: 'Precision', value: '95.3%', trend: '+2.7%' },
  { label: 'Recall', value: '94.1%', trend: '+3.1%' },
  { label: 'F1-score', value: '95.6%', trend: '+3.4%' },
]

const history: HistoryItem[] = [
  { id: 'DR-1024', label: 'Calculus', confidence: 0.96, date: 'Today • 09:42', status: 'Reviewed' },
  { id: 'DR-1017', label: 'Gingivitis', confidence: 0.9, date: 'Yesterday • 17:18', status: 'Pending' },
  { id: 'DR-1006', label: 'Dental Caries', confidence: 0.88, date: 'Mon • 14:10', status: 'Flagged' },
  { id: 'DR-998', label: 'Hypodontia', confidence: 0.81, date: 'Sun • 11:08', status: 'Reviewed' },
]

const patientProfile = {
  name: 'Dr. Aisha Rahman',
  clinic: 'SmileCare Dental Lab',
  role: 'Lead Oral Diagnostics',
  email: 'aisha@smilecare.ai',
  phone: '+1 (415) 555-0147',
  avatar: 'AR',
}

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Dashboard', to: '/dashboard' },
  { label: 'Results', to: '/result' },
  { label: 'Profile', to: '/profile' },
]

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-100 text-slate-900">
        <SiteShell />
      </div>
    </BrowserRouter>
  )
}

function SiteShell() {
  return (
    <>
      <header className="border-b border-slate-200/80 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <NavLink to="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-navy-700 to-teal-500 text-sm font-bold text-white shadow-soft">
              DV
            </div>
            <div>
              <div className="text-lg font-semibold text-navy-900">DentalVision</div>
              <div className="text-xs text-slate-500">AI Diagnostics Platform</div>
            </div>
          </NavLink>

          <nav className="hidden items-center gap-6 md:flex">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `text-sm font-medium transition ${isActive ? 'text-navy-700' : 'text-slate-600 hover:text-navy-700'}`
                }
              >
                {item.label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            <NavLink
              to="/login"
              className="rounded-full border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-navy-200 hover:text-navy-700"
            >
              Sign in
            </NavLink>
            <NavLink
              to="/signup"
              className="rounded-full bg-navy-800 px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:bg-navy-700"
            >
              Get started
            </NavLink>
          </div>
        </div>
      </header>

      <main>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<AuthPage mode="login" />} />
          <Route path="/signup" element={<AuthPage mode="signup" />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/result" element={<PredictionResultPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
      </main>
    </>
  )
}

function LandingPage() {
  const highlights = [
    'AI-assisted oral disease assessment',
    'Deployable ML pipeline',
    'Secure patient data workflow',
  ]

  return (
    <div className="bg-[radial-gradient(circle_at_top,_rgba(34,211,238,0.08),_transparent_40%),linear-gradient(180deg,#edf7ff_0%,#ffffff_35%,#f8fafc_100%)]">
      <section className="mx-auto grid max-w-7xl gap-10 px-4 py-16 sm:px-6 lg:grid-cols-[1.15fr_0.85fr] lg:px-8 lg:py-24">
        <div className="flex flex-col justify-center">
          <div className="mb-4 inline-flex w-fit items-center gap-2 rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.12em] text-teal-700">
            Precision oral health intelligence
          </div>
          <h1 className="max-w-xl text-4xl font-bold leading-tight text-navy-900 sm:text-5xl">
            Transform dental imaging into actionable clinical insights.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-slate-600">
            DentalVision helps clinicians detect common oral conditions with explainable AI, confident triage workflows, and secure image review pipelines.
          </p>

          <div className="mt-8 flex flex-wrap gap-4">
            <NavLink
              to="/dashboard"
              className="rounded-full bg-navy-800 px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-navy-700"
            >
              Open dashboard
            </NavLink>
            <NavLink
              to="/signup"
              className="rounded-full border border-slate-200 bg-white px-6 py-3 text-sm font-semibold text-slate-700 transition hover:border-navy-200 hover:text-navy-700"
            >
              Request demo
            </NavLink>
          </div>

          <div className="mt-8 flex flex-wrap gap-6 text-sm text-slate-600">
            {highlights.map((item) => (
              <div key={item} className="flex items-center gap-2">
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-teal-500" />
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="relative">
          <div className="absolute -left-10 top-10 h-40 w-40 rounded-full bg-teal-200/70 blur-3xl" />
          <div className="absolute -right-8 bottom-8 h-44 w-44 rounded-full bg-navy-300/70 blur-3xl" />
          <div className="relative overflow-hidden rounded-[32px] border border-slate-200 bg-white p-4 shadow-soft">
            <div className="rounded-[24px] bg-gradient-to-br from-navy-900 to-navy-700 p-5 text-white">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Live analysis</p>
                  <h2 className="mt-2 text-2xl font-semibold">Treatment risk overview</h2>
                </div>
                <div className="rounded-full bg-teal-400/20 px-3 py-1 text-xs font-semibold text-teal-200">94.8% avg confidence</div>
              </div>

              <div className="mt-8 grid grid-cols-2 gap-4">
                <StatCard label="Cases analyzed" value="1,248" />
                <StatCard label="High risk" value="84" />
                <StatCard label="Accuracy" value="96.8%" />
                <StatCard label="Avg. review" value="4.2m" />
              </div>
            </div>

            <div className="mt-5 rounded-2xl border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-center justify-between text-sm text-slate-600">
                <span>Condition spread</span>
                <span className="font-semibold text-navy-700">This month</span>
              </div>
              <div className="mt-4 space-y-3">
                {[
                  { label: 'Calculus', value: 78 },
                  { label: 'Dental caries', value: 62 },
                  { label: 'Gingivitis', value: 93 },
                  { label: 'Hypodontia', value: 41 },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="mb-1 flex justify-between text-xs text-slate-500">
                      <span>{item.label}</span>
                      <span>{item.value}%</span>
                    </div>
                    <div className="h-2.5 rounded-full bg-slate-200">
                      <div className="h-full rounded-full bg-gradient-to-r from-teal-400 to-navy-700" style={{ width: `${item.value}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
        <div className="grid gap-6 md:grid-cols-3">
          {[
            ['Explainable AI', 'Class activation overlays help clinicians review model attention regions with context.'],
            ['Operational monitoring', 'Track performance, uncertainty, and review queue status in one secure interface.'],
            ['Secure workflows', 'Upload, validate, and interpret studies without exposing patient content publicly.'],
          ].map(([title, description]) => (
            <div key={title} className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-teal-100 to-navy-100 text-lg font-semibold text-navy-800">
                {title.slice(0, 1)}
              </div>
              <h3 className="text-xl font-semibold text-navy-900">{title}</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">{description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

function AuthPage({ mode }: { mode: 'login' | 'signup' }) {
  const isSignup = mode === 'signup'

  return (
    <div className="mx-auto flex max-w-6xl items-center justify-center px-4 py-16 sm:px-6 lg:px-8">
      <div className="grid w-full overflow-hidden rounded-[32px] border border-slate-200 bg-white shadow-soft lg:grid-cols-2">
        <div className="bg-gradient-to-br from-navy-900 via-navy-800 to-teal-600 p-8 text-white lg:p-12">
          <div className="mb-8 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 text-lg font-bold">
            DV
          </div>
          <h2 className="text-3xl font-semibold">{isSignup ? 'Create a secure clinical workspace' : 'Welcome back'}</h2>
          <p className="mt-4 max-w-md text-sm leading-7 text-slate-200">
            Access your oral AI dashboard, review patient image studies, and monitor model confidence in a privacy-conscious workflow.
          </p>

          <div className="mt-10 space-y-4 text-sm text-slate-200">
            {['Protected patient data controls', 'Explainable AI review queue', 'Clinical-ready reporting'].map((item) => (
              <div key={item} className="flex items-center gap-3">
                <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-white/10">✓</span>
                {item}
              </div>
            ))}
          </div>
        </div>

        <div className="p-8 lg:p-12">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">{isSignup ? 'Sign up' : 'Sign in'}</p>
              <h3 className="mt-2 text-3xl font-semibold text-navy-900">{isSignup ? 'Set up your account' : 'Access your dashboard'}</h3>
            </div>
          </div>

          <form className="space-y-5">
            {isSignup && (
              <label className="block text-sm font-medium text-slate-700">
                Full name
                <input className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-teal-400 focus:bg-white" placeholder="Dr. Aisha Rahman" />
              </label>
            )}

            <label className="block text-sm font-medium text-slate-700">
              Work email
              <input className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-teal-400 focus:bg-white" placeholder="name@clinic.org" />
            </label>

            <label className="block text-sm font-medium text-slate-700">
              Password
              <input type="password" className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-teal-400 focus:bg-white" placeholder="••••••••" />
            </label>

            {isSignup && (
              <label className="block text-sm font-medium text-slate-700">
                Clinic / institution
                <input className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 outline-none transition focus:border-teal-400 focus:bg-white" placeholder="SmileCare Dental Lab" />
              </label>
            )}

            <button
              type="button"
              className="w-full rounded-xl bg-navy-800 px-4 py-3 text-sm font-semibold text-white transition hover:bg-navy-700"
            >
              {isSignup ? 'Create account' : 'Sign in'}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-600">
            {isSignup ? 'Already have an account?' : 'Need a new account?'}{' '}
            <NavLink to={isSignup ? '/login' : '/signup'} className="font-semibold text-navy-700">
              {isSignup ? 'Sign in' : 'Create account'}
            </NavLink>
          </div>
        </div>
      </div>
    </div>
  )
}

function DashboardPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string>('')
  const [imageError, setImageError] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const navigate = useNavigate()

  const fileLabel = useMemo(() => selectedFile ? selectedFile.name : 'No file selected', [selectedFile])

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null
    if (!file) {
      setSelectedFile(null)
      setPreviewUrl('')
      return
    }

    if (!file.type.startsWith('image/')) {
      setImageError('Please upload a valid image file for dental analysis.')
      return
    }

    if (file.size > 8 * 1024 * 1024) {
      setImageError('Image file exceeds the 8 MB limit.')
      return
    }

    setSelectedFile(file)
    setImageError('')
    setPreviewUrl(URL.createObjectURL(file))
  }

  const handleAnalyze = () => {
    if (!selectedFile) {
      setImageError('Choose an image before running the diagnostic workflow.')
      return
    }

    setIsAnalyzing(true)
    window.setTimeout(() => {
      setIsAnalyzing(false)
      navigate('/result', {
        state: {
          previewUrl,
          prediction: {
            label: 'Gingivitis',
            confidence: 0.94,
            confidenceLabel: 'High confidence',
            heatmap: 'Teal-signal cluster around gumline and soft tissue',
          },
          metadata: {
            model: 'MobileNet-v2',
            risk: 'Moderate',
            time: '1.2s',
          },
        },
      })
    }, 1500)
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Overview</p>
          <h1 className="mt-2 text-3xl font-semibold text-navy-900">Clinical dashboard</h1>
        </div>
        <button className="rounded-full bg-navy-800 px-5 py-3 text-sm font-medium text-white shadow-soft hover:bg-navy-700">
          Export report
        </button>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {modelMetrics.map((metric) => (
          <div key={metric.label} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-soft">
            <p className="text-sm text-slate-500">{metric.label}</p>
            <div className="mt-4 flex items-end justify-between">
              <span className="text-3xl font-semibold text-navy-900">{metric.value}</span>
              <span className="rounded-full bg-teal-100 px-2 py-1 text-xs font-semibold text-teal-700">{metric.trend}</span>
            </div>
          </div>
        ))}
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Upload</p>
              <h2 className="mt-2 text-2xl font-semibold text-navy-900">Image review</h2>
            </div>
            <button className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.12em] text-slate-600">
              Secure upload
            </button>
          </div>

          <div className="rounded-3xl border-2 border-dashed border-slate-200 bg-slate-50 p-6">
            <label className="flex cursor-pointer flex-col items-center justify-center gap-4 text-center">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-navy-100 text-2xl text-navy-700">+</div>
              <div>
                <p className="text-lg font-medium text-slate-800">Drop an oral image here</p>
                <p className="text-sm text-slate-500">PNG, JPG, or WEBP up to 8 MB</p>
              </div>
              <input type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
            </label>
          </div>

          {imageError && <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{imageError}</div>}

          {previewUrl && (
            <div className="mt-6 overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
              <img src={previewUrl} alt="Uploaded oral image preview" className="h-72 w-full object-cover" />
            </div>
          )}

          <div className="mt-6 flex items-center justify-between gap-4 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
            <div>
              <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Selected file</p>
              <p className="mt-1 text-sm font-medium text-slate-700">{fileLabel}</p>
            </div>
            <button
              type="button"
              onClick={handleAnalyze}
              className="rounded-full bg-teal-500 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-teal-600 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isAnalyzing}
            >
              {isAnalyzing ? 'Analyzing…' : 'Analyze image'}
            </button>
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Review queue</p>
            <div className="mt-4 space-y-4">
              {[
                ['Urgent review', '12 cases'],
                ['Scheduled today', '24 cases'],
                ['Awaiting validation', '6 cases'],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                  <span className="font-medium text-slate-700">{label}</span>
                  <span className="rounded-full bg-white px-2.5 py-1 text-xs font-semibold text-navy-700">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Model status</p>
            <div className="mt-4 rounded-2xl bg-gradient-to-r from-navy-900 to-teal-600 p-4 text-white">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-200">System health</span>
                <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs font-medium text-emerald-200">Stable</span>
              </div>
              <div className="mt-5 text-3xl font-semibold">99.2%</div>
              <div className="mt-2 text-sm text-slate-200">Model uptime and validation checks</div>
            </div>
          </div>
        </div>
      </section>

      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">History</p>
            <h2 className="mt-2 text-2xl font-semibold text-navy-900">Prediction history</h2>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-slate-600">
              <tr>
                <th className="px-4 py-3 font-medium">ID</th>
                <th className="px-4 py-3 font-medium">Condition</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Date</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {history.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3 font-medium text-slate-800">{item.id}</td>
                  <td className="px-4 py-3 text-slate-700">{item.label}</td>
                  <td className="px-4 py-3 text-slate-700">{item.confidence.toFixed(2)}</td>
                  <td className="px-4 py-3 text-slate-700">{item.date}</td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-teal-100 px-2.5 py-1 text-xs font-semibold text-teal-700">{item.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}

function PredictionResultPage() {
  const location = useLocation()
  const state = location.state as {
    previewUrl?: string
    prediction?: PredictionEstimate
    metadata?: { model: string; risk: string; time: string }
  } | undefined

  const prediction = state?.prediction ?? {
    label: 'Calculus',
    confidence: 0.96,
    confidenceLabel: 'High confidence',
    heatmap: 'Strong activation along the enamel surface and calculus cluster',
  }

  const previewUrl = state?.previewUrl ?? 'https://images.unsplash.com/photo-1588776814546-da5e4aef00b4?auto=format&fit=crop&w=1200&q=80'

  const metadata = state?.metadata ?? { model: 'MobileNet-v2', risk: 'Moderate', time: '1.2s' }

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Analysis</p>
          <h1 className="mt-2 text-3xl font-semibold text-navy-900">Prediction result</h1>
        </div>
        <div className="rounded-full bg-emerald-100 px-3 py-2 text-sm font-medium text-emerald-700">{prediction.confidenceLabel}</div>
      </div>

      <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <div className="mb-5 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Input image</p>
              <h2 className="mt-2 text-2xl font-semibold text-navy-900">Oral radiograph review</h2>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.14em] text-slate-600">Image #DU-2041</span>
          </div>

          <div className="overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <img src={previewUrl} alt="Uploaded oral image" className="h-[420px] w-full object-cover" />
          </div>
        </div>

        <div className="space-y-6">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Prediction</p>
            <div className="mt-4 flex items-center justify-between">
              <div>
                <div className="text-3xl font-semibold text-navy-900">{prediction.label}</div>
                <div className="mt-2 text-sm text-slate-500">Confidence score</div>
              </div>
              <div className="text-4xl font-bold text-teal-600">{(prediction.confidence * 100).toFixed(1)}%</div>
            </div>
            <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-200">
              <div className="h-full rounded-full bg-gradient-to-r from-teal-400 to-navy-700" style={{ width: `${(prediction.confidence * 100).toFixed(0)}%` }} />
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Case metadata</p>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="flex justify-between"><span>Model</span><span className="font-medium text-slate-800">{metadata.model}</span></div>
              <div className="flex justify-between"><span>Risk band</span><span className="font-medium text-slate-800">{metadata.risk}</span></div>
              <div className="flex justify-between"><span>Inference time</span><span className="font-medium text-slate-800">{metadata.time}</span></div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Explainability</p>
              <h2 className="mt-2 text-2xl font-semibold text-navy-900">Grad-CAM visualization</h2>
            </div>
          </div>

          <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-slate-100">
            <img src={previewUrl} alt="Grad-CAM overlay preview" className="h-[320px] w-full object-cover opacity-70" />
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_35%,rgba(255,196,0,0.55),transparent_18%),radial-gradient(circle_at_58%_42%,rgba(34,211,238,0.45),transparent_22%),linear-gradient(135deg,rgba(13,30,54,0.2),rgba(13,30,54,0.4))]" />
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-600">{prediction.heatmap}</p>
        </div>

        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Confidence breakdown</p>
          <div className="mt-6 space-y-5">
            {[
              ['Calculus', 0.18],
              ['Dental Caries', 0.12],
              ['Gingivitis', 0.46],
              ['Hypodontia', 0.09],
              ['Mouth Ulcer', 0.15],
            ].map(([label, value]) => (
              <div key={label as string}>
                <div className="mb-2 flex justify-between text-sm text-slate-600">
                  <span>{label as string}</span>
                  <span className="font-medium text-navy-800">{Number(value) * 100}%</span>
                </div>
                <div className="h-2.5 rounded-full bg-slate-200">
                  <div className="h-full rounded-full bg-gradient-to-r from-navy-700 via-teal-400 to-emerald-400" style={{ width: `${Number(value) * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

function ProfilePage() {
  return (
    <div className="mx-auto max-w-6xl space-y-8 px-4 py-10 sm:px-6 lg:px-8">
      <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="flex items-center gap-5">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-navy-800 to-teal-500 text-xl font-semibold text-white">{patientProfile.avatar}</div>
            <div>
              <h1 className="text-3xl font-semibold text-navy-900">{patientProfile.name}</h1>
              <p className="text-sm text-slate-500">{patientProfile.role}</p>
            </div>
          </div>
          <button className="rounded-full border border-slate-200 bg-slate-50 px-4 py-2 text-sm font-medium text-slate-700">Edit profile</button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Account</p>
          <div className="mt-5 space-y-4 text-sm text-slate-600">
            <div className="flex justify-between border-b border-slate-200 pb-3"><span>Clinic</span><span className="font-medium text-slate-800">{patientProfile.clinic}</span></div>
            <div className="flex justify-between border-b border-slate-200 pb-3"><span>Email</span><span className="font-medium text-slate-800">{patientProfile.email}</span></div>
            <div className="flex justify-between border-b border-slate-200 pb-3"><span>Phone</span><span className="font-medium text-slate-800">{patientProfile.phone}</span></div>
            <div className="flex justify-between"><span>Access role</span><span className="font-medium text-slate-800">Clinician</span></div>
          </div>
        </div>

        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-soft">
          <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Security</p>
          <div className="mt-5 space-y-4">
            {[
              ['Two-factor authentication', 'Enabled'],
              ['Audit log retention', '365 days'],
              ['Data residency', 'US-East'],
            ].map(([label, value]) => (
              <div key={label as string} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                <span className="text-sm text-slate-600">{label as string}</span>
                <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">{value as string}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-300">{label}</p>
      <p className="mt-3 text-2xl font-semibold text-white">{value}</p>
    </div>
  )
}

export default App
