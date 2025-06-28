import 'regenerator-runtime/runtime';
import { useEffect } from 'react';
import { useContext } from 'react';
import { AuthContext } from "../../Providers/AuthProvider";
import AOS from 'aos';
import 'aos/dist/aos.css';
import { Link } from 'react-router-dom';
import { useRef } from 'react';

export default function Home() {
  useEffect(() => {
    AOS.init({
      duration: 2000,
      once: true,
    });
  }, []);

  const { user } = useContext(AuthContext);

  useEffect(() => {
    console.log(user);
  }, [user]);

  const demoSectionRef = useRef(null);
  
  // Custom slow scroll function
  const slowScrollToRef = (ref, duration = 2000) => {
    if (!ref.current) {
            console.error("Demo section ref is null");
            return;
          }

  const targetPosition = ref.current.getBoundingClientRect().top + window.scrollY;
  const startPosition = window.scrollY;
  const distance = targetPosition - startPosition;
  let startTime = null;

  const easeInOutQuad = (t) => t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
  
  const animation = (currentTime) => {
    if (startTime === null) startTime = currentTime;
    const timeElapsed = currentTime - startTime;
    const progress = Math.min(timeElapsed / duration, 1); // Cap at 1
    const easeProgress = easeInOutQuad(progress);

    window.scrollTo(0, startPosition + distance * easeProgress);

    if (timeElapsed < duration) {
      requestAnimationFrame(animation);
    }
  };

  requestAnimationFrame(animation);
};

const handleScrollToDemo = () => {
  slowScrollToRef(demoSectionRef, 2000); // 2000ms = 2 seconds
};

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-screen flex items-center justify-center bg-white">
        <div className="container mx-auto px-4 relative z-10">
          <div className="flex flex-col lg:flex-row items-center gap-12">
            <div className="lg:w-1/2 text-center lg:text-left" data-aos="fade-right">
              <div className="inline-block bg-black text-white px-4 py-2 rounded-full text-sm font-medium mb-4">
                🚀 AI-Powered Infrastructure Guardian
              </div>
              <h1 className="text-5xl md:text-6xl font-bold text-black mb-6 leading-tight">
                SRE Agent: <span className="text-gray-600">Pre-Deployment</span> & Cost-Aware Infrastructure Guardian
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Reduce post-deployment issues and identify cost inefficiencies with AI-powered automated pre-checks and continuous monitoring
              </p>
              <button className="bg-black hover:bg-gray-800 text-white px-8 py-4 rounded-full text-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
                onClick={handleScrollToDemo}>
                Try Demo
              </button>
            </div>
            <div className="lg:w-1/2" data-aos="fade-left">
              <div className="relative">
                <div className="bg-gray-50 border-2 border-gray-200 rounded-2xl p-8">
                  <div className="space-y-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                      <span className="text-green-600 font-mono text-sm">✓ Configuration validated</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
                      <span className="text-yellow-600 font-mono text-sm">⚠ Cost optimization found</span>
                    </div>
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-black rounded-full animate-pulse"></div>
                      <span className="text-gray-700 font-mono text-sm">📊 Monitoring active</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Section */}
      <section className="py-20 bg-gray-50"
        ref={demoSectionRef}>
        <div className="container mx-auto px-4" data-aos="fade-up">
          <div className="max-w-4xl mx-auto text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">Experience AI-Powered SRE Analysis</h2>
            <p className="text-gray-600 text-lg">Upload your deployment configuration and get instant analysis</p>
          </div>
          <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-lg p-8 border-2 border-solid border-gray-300 hover:border-black transition-colors">
            <div className="text-center py-8">
              <div className="bg-gray-50 rounded-lg p-6 mb-6 border border-gray-200">
                <div className="flex items-center justify-center mb-4">
                  <svg className="w-12 h-12 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <p className="text-gray-700 mb-4">
                  Drop your YAML/JSON deployment configuration here for instant AI analysis
                </p>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 hover:border-black transition-colors cursor-pointer">
                  <p className="text-gray-600">Click to upload or drag and drop</p>
                  <p className="text-sm text-gray-500 mt-2">Supports .yaml, .yml, .json files</p>
                </div>
              </div>
              <Link
                to={user ? "/agent" : "/login"}
                className="bg-black text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-800 transition-colors"
              >
                {user ? "Start Analysis" : "Sign In to Continue"}
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* MVP Features */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-black">MVP Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            
            {/* Pre-Deployment Check */}
            <div
              data-aos="fade-up"
              className="bg-gray-50 p-8 rounded-xl border-2 border-gray-200 hover:shadow-xl hover:border-black transition-all"
            >
              <div className="w-16 h-16 bg-black rounded-xl flex items-center justify-center text-white mb-6">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold mb-4 text-black">Pre-Deployment SRE Check</h3>
              <p className="text-gray-600 mb-4">
                AI analyzes deployment configurations against SRE best practices and identifies common pitfalls
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Configuration validation</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Security misconfiguration detection</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Resource limit analysis</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Slack/Teams integration</li>
              </ul>
            </div>

            {/* Cost Monitoring */}
            <div
              data-aos="fade-up"
              data-aos-delay="200"
              className="bg-gray-50 p-8 rounded-xl border-2 border-gray-200 hover:shadow-xl hover:border-black transition-all"
            >
              <div className="w-16 h-16 bg-gray-700 rounded-xl flex items-center justify-center text-white mb-6">
                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <h3 className="text-2xl font-semibold mb-4 text-black">Cost Monitoring & Optimization</h3>
              <p className="text-gray-600 mb-4">
                Continuous monitoring of resource utilization with AI-powered cost optimization suggestions
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Utilization analysis</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Cost-saving recommendations</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Estimated savings calculation</li>
                <li className="flex items-center"><span className="text-green-600 mr-2">✓</span>Automated alerts</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-black">How It Works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: 1,
                title: "Upload Configuration",
                description: "Paste your YAML/JSON deployment configuration or use our CLI tool",
                icon: "📤"
              },
              {
                step: 2,
                title: "AI Analysis",
                description: "Our AI analyzes configurations against SRE best practices and identifies cost inefficiencies",
                icon: "🤖"
              },
              {
                step: 3,
                title: "Get Actionable Insights",
                description: "Receive detailed reports via Slack/Teams with specific recommendations and estimated savings",
                icon: "📊"
              }
            ].map((item) => (
              <div
                key={item.step}
                data-aos="zoom-in"
                data-aos-delay={item.step * 100}
                className="bg-white p-8 rounded-xl hover:shadow-xl transition-shadow border-2 border-gray-200 hover:border-black"
              >
                <div className="w-16 h-16 bg-black rounded-xl flex items-center justify-center text-white mb-6 text-2xl">
                  {item.icon}
                </div>
                <h3 className="text-xl font-semibold mb-4 text-black">Step {item.step}: {item.title}</h3>
                <p className="text-gray-600">
                  {item.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Integration Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4" data-aos="fade-up">
          <div className="max-w-4xl mx-auto text-center mb-16">
            <h2 className="text-4xl font-bold text-black mb-4">Seamless Integrations</h2>
            <p className="text-gray-600 text-lg">Connect with your existing workflow tools</p>
          </div>
          <div className="flex flex-wrap justify-center items-center gap-8">
            <div className="bg-gray-100 border-2 border-gray-200 hover:border-black transition-colors px-6 py-3 rounded-lg font-medium text-black">Slack</div>
            <div className="bg-gray-100 border-2 border-gray-200 hover:border-black transition-colors px-6 py-3 rounded-lg font-medium text-black">Microsoft Teams</div>
            <div className="bg-gray-100 border-2 border-gray-200 hover:border-black transition-colors px-6 py-3 rounded-lg font-medium text-black">Notion</div>
            <div className="bg-gray-100 border-2 border-gray-200 hover:border-black transition-colors px-6 py-3 rounded-lg font-medium text-black">Google Sheets</div>
            <div className="bg-gray-100 border-2 border-gray-200 hover:border-black transition-colors px-6 py-3 rounded-lg font-medium text-black">CLI Tool</div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-black py-20">
        <div className="container mx-auto px-4 text-center" data-aos="fade-up">
          <h2 className="text-4xl font-bold text-white mb-8">Ready to Guard Your Infrastructure?</h2>
          <p className="text-xl text-gray-300 mb-12 max-w-2xl mx-auto">
            Join the future of SRE with AI-powered pre-deployment checks and cost optimization
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-black px-8 py-4 rounded-full text-lg font-semibold hover:bg-gray-100 transition-colors transform hover:scale-105">
              Start Free Trial
            </button>
            <button className="border-2 border-white text-white px-8 py-4 rounded-full text-lg font-semibold hover:bg-white hover:text-black transition-colors">
              Schedule Demo
            </button>
          </div>
          <p className="text-gray-400 text-sm mt-6">No credit card required • 14-day free trial</p>
        </div>
      </section>
    </div>
  );
}
