import { useState, useRef, useEffect } from 'react';
import { BookOpen, Zap, CheckCircle, XCircle, ArrowRight, ArrowLeft, RefreshCw, Trophy, Volume2, Eye, RotateCcw, Image as ImageIcon } from 'lucide-react';

// --- TIPOS ---
interface QuizQuestion {
  questionId: number;
  questionText: string;
  options: string[];
  correctOptionIndex: number;
}

interface Slide {
  id: number;
  title: string;
  text: string;
  imagePrompt: string;
  imageUrl: string;
  audioUrl: string;
}

interface LearningContent {
  slides: Slide[];
  quiz: QuizQuestion[];
}

function App() {
  const [topic, setTopic] = useState('');
  const [level, setLevel] = useState('Iniciante');
  
  // Estados de Carregamento
  const [loading, setLoading] = useState(false);
  const [isPreloadingImages, setIsPreloadingImages] = useState(false);
  
  const [content, setContent] = useState<LearningContent | null>(null);
  const [error, setError] = useState('');

  // Navegação
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [viewMode, setViewMode] = useState<'slides' | 'quiz'>('slides');

  // Quiz
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<number, number>>({});
  const [isQuizFinished, setIsQuizFinished] = useState(false);
  const [showAnswerKey, setShowAnswerKey] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (content && viewMode === 'slides' && !isPreloadingImages && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.load();
      
      
      audioRef.current.playbackRate = 1.50;
      

      audioRef.current.play().catch(e => console.log("Autoplay bloqueado:", e));
    }
  }, [currentSlideIndex, content, viewMode, isPreloadingImages]);

  // Função Auxiliar: Pré-carregar Imagens
  const preloadImages = async (slides: Slide[]) => {
    setIsPreloadingImages(true);
    const promises = slides.map((slide) => {
      return new Promise((resolve) => {
        const img = new Image();
        img.src = slide.imageUrl;
        img.onload = resolve;
        img.onerror = resolve; 
      });
    });
    await Promise.all(promises);
    setIsPreloadingImages(false);
  };

  const handleGenerate = async () => {
    if (!topic.trim()) return alert('Por favor, digite um tópico!');
    
    setLoading(true); setError(''); setContent(null);
    setCurrentSlideIndex(0); setViewMode('slides');
    setCurrentQuizIndex(0); setUserAnswers({}); 
    setIsQuizFinished(false); setShowAnswerKey(false);

    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
      const response = await fetch(`${apiUrl}/api/generate-learning`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, level }),
      });

      if (!response.ok) throw new Error('Erro ao conectar com o servidor');

      const data: LearningContent = await response.json();
      
      setLoading(false); 
      await preloadImages(data.slides); 
      setContent(data); 
      
    } catch (err) {
      console.error(err);
      setError('Erro: Verifique se o backend está rodando.');
      setLoading(false);
      setIsPreloadingImages(false);
    }
  };

  const nextSlide = () => {
    if (content && currentSlideIndex < content.slides.length - 1) {
      setCurrentSlideIndex(prev => prev + 1);
    } else {
      setViewMode('quiz');
    }
  };

  const prevSlide = () => {
    if (currentSlideIndex > 0) setCurrentSlideIndex(prev => prev - 1);
  };

  const handleSelectOption = (idx: number) => setUserAnswers(prev => ({ ...prev, [currentQuizIndex]: idx }));
  const handleNextQuestion = () => currentQuizIndex < (content?.quiz.length || 0) - 1 ? setCurrentQuizIndex(prev => prev + 1) : setIsQuizFinished(true);
  const calculateScore = () => content ? content.quiz.reduce((acc, q, idx) => userAnswers[idx] === q.correctOptionIndex ? acc + 1 : acc, 0) : 0;
  
  const resetQuiz = () => {
    setIsQuizFinished(false);
    setCurrentQuizIndex(0);
    setUserAnswers({});
    setShowAnswerKey(false);
  };

  const getMotivationMessage = (score: number, total: number) => {
    const p = (score / total) * 100;
    if (p === 100) return { text: "Perfeito! Você dominou o assunto!", color: "text-teal-600" };
    if (p >= 70) return { text: "Excelente! Você aprendeu muito.", color: "text-teal-600" };
    return { text: "Bom esforço! Que tal rever os slides?", color: "text-orange-500" };
  };

  const isProcessing = loading || isPreloadingImages;

  return (
    <div className="min-h-screen bg-white font-sans selection:bg-teal-100 pb-20">
      <div className="fixed inset-0 -z-10 bg-white [background:radial-gradient(125%_125%_at_50%_10%,#fff_40%,#63e_100%)] opacity-5"></div>

      <header className="flex items-center justify-between px-6 py-5 max-w-7xl mx-auto">
        <div className="flex items-center gap-2 text-teal-600">
          <div className="bg-teal-500 text-white p-1.5 rounded-lg"><BookOpen size={20} strokeWidth={3} /></div>
          <span className="text-xl font-bold text-slate-800">EduGen</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 pt-8">
        
        {(!content || isProcessing) && (
          <div className="animate-in fade-in zoom-in duration-500 max-w-2xl mx-auto">
            {!content && (
                <div className="text-center mb-12">
                <h1 className="text-4xl md:text-6xl font-extrabold text-slate-900 mb-4">
                    Aprendizado Gerado por <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-teal-400">IA</span>
                </h1>
                <p className="text-lg text-slate-500">Gere slides explicativos e quizzes sobre qualquer tema.</p>
                </div>
            )}

            {!content && (
                <div className="bg-white p-8 rounded-3xl shadow-xl border border-slate-100">
                <div className="mb-6">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">O que você quer aprender?</label>
                    <input type="text" placeholder="Ex: A Revolução Industrial" className="w-full px-4 py-3.5 rounded-xl border border-slate-200 focus:border-teal-500 outline-none transition" value={topic} onChange={(e) => setTopic(e.target.value)} disabled={isProcessing} />
                </div>
                <div className="mb-8">
                    <label className="block text-sm font-semibold text-slate-700 mb-2">Nível</label>
                    <select className="w-full px-4 py-3.5 rounded-xl border border-slate-200 bg-white" value={level} onChange={(e) => setLevel(e.target.value)} disabled={isProcessing}>
                        <option>Iniciante</option><option>Intermediário</option><option>Avançado</option>
                    </select>
                </div>
                <button onClick={handleGenerate} disabled={isProcessing} className="w-full bg-gradient-to-r from-blue-500 to-teal-400 hover:to-teal-500 text-white font-bold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2 transition-all disabled:opacity-70">
                    {loading ? (
                        <span className="flex items-center gap-2">
                            <span className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></span>
                            Escrevendo Roteiro...
                        </span>
                    ) : isPreloadingImages ? (
                        <span className="flex items-center gap-2">
                            <ImageIcon size={20} className="animate-pulse" />
                            Gerando Imagens...
                        </span>
                    ) : (
                        <><Zap size={20} /> Iniciar Aula</>
                    )}
                </button>
                {error && <div className="mt-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-100">{error}</div>}
                </div>
            )}
            
            {isProcessing && content && (
                 <div className="flex flex-col items-center justify-center py-20">
                    <div className="animate-spin h-12 w-12 border-4 border-teal-500 border-t-transparent rounded-full mb-4"></div>
                    <p className="text-slate-600 font-medium text-lg animate-pulse">
                        {isPreloadingImages ? "Finalizando visuais..." : "Gerando conteúdo..."}
                    </p>
                 </div>
            )}
          </div>
        )}

        {content && !isProcessing && (
          <div className="animate-in slide-in-from-bottom-8 duration-700">
            
            <div className="flex justify-between items-center mb-6">
                <button onClick={() => setContent(null)} className="text-slate-500 hover:text-teal-600 flex items-center gap-1 font-medium transition"><RefreshCw size={16} /> Novo Tópico</button>
                {viewMode === 'slides' && (
                    <span className="bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-sm font-bold">
                        Slide {currentSlideIndex + 1} de {content.slides.length}
                    </span>
                )}
            </div>

            {viewMode === 'slides' && (
                <div className="bg-white rounded-3xl overflow-hidden shadow-2xl border border-slate-100">
                    <div className="relative aspect-video bg-slate-100 overflow-hidden group">
                        <img 
                            key={content.slides[currentSlideIndex].imageUrl}
                            src={content.slides[currentSlideIndex].imageUrl} 
                            alt={content.slides[currentSlideIndex].title} 
                            className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                        <div className="absolute bottom-0 left-0 p-8 w-full">
                            <h2 className="text-3xl font-bold text-white mb-2">{content.slides[currentSlideIndex].title}</h2>
                        </div>
                    </div>
                    <div className="p-8">
                        <div className="flex items-start gap-4 mb-6">
                             <div className="bg-teal-100 p-3 rounded-xl text-teal-600 shrink-0 mt-1"><Volume2 size={24} /></div>
                             <div>
                                <p className="text-slate-700 text-lg leading-relaxed mb-4 font-medium">{content.slides[currentSlideIndex].text}</p>
                                <audio ref={audioRef} controls className="w-full h-8 accent-teal-500" src={content.slides[currentSlideIndex].audioUrl}>Seu navegador não suporta áudio.</audio>
                             </div>
                        </div>
                        <div className="flex justify-between items-center mt-8 pt-6 border-t border-slate-100">
                            <button onClick={prevSlide} disabled={currentSlideIndex === 0} className="flex items-center gap-2 text-slate-500 hover:text-slate-800 disabled:opacity-30 disabled:cursor-not-allowed font-semibold px-4 py-2 rounded-lg hover:bg-slate-50 transition"><ArrowLeft size={20} /> Anterior</button>
                            <button onClick={nextSlide} className="bg-slate-900 hover:bg-slate-800 text-white px-8 py-3 rounded-xl font-bold flex items-center gap-2 transition shadow-lg hover:shadow-xl">
                                {currentSlideIndex === content.slides.length - 1 ? 'Ir para o Quiz' : 'Próximo Slide'} <ArrowRight size={20} />
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {viewMode === 'quiz' && (
                <div className="bg-white rounded-3xl p-8 shadow-xl border border-slate-100 animate-in zoom-in-95">
                    
                    {!isQuizFinished && (
                        <div>
                            <div className="flex items-center justify-between mb-8">
                                <h2 className="text-2xl font-bold text-slate-800 flex gap-2"><CheckCircle className="text-teal-500" /> Quiz de Fixação</h2>
                                <span className="text-sm font-bold text-slate-400 bg-slate-100 px-3 py-1 rounded-full">Questão {currentQuizIndex + 1}/{content.quiz.length}</span>
                            </div>
                            <div className="w-full bg-slate-100 h-2 rounded-full mb-8"><div className="bg-teal-500 h-full transition-all" style={{ width: `${((currentQuizIndex + 1) / content.quiz.length) * 100}%` }}></div></div>
                            
                            <h3 className="text-xl font-semibold text-slate-800 mb-6">{content.quiz[currentQuizIndex].questionText}</h3>
                            <div className="grid gap-3 mb-8">
                                {content.quiz[currentQuizIndex].options.map((opt, idx) => (
                                    <button key={idx} onClick={() => handleSelectOption(idx)} className={`w-full text-left p-4 rounded-xl border-2 transition-all ${userAnswers[currentQuizIndex] === idx ? 'border-teal-500 bg-teal-50' : 'border-slate-100 hover:bg-slate-50'}`}>
                                        {opt}
                                    </button>
                                ))}
                            </div>
                            <div className="flex justify-between">
                                <button onClick={() => setViewMode('slides')} className="text-slate-500 underline text-sm">Voltar aos Slides</button>
                                <button onClick={handleNextQuestion} disabled={userAnswers[currentQuizIndex] === undefined} className="bg-teal-600 hover:bg-teal-700 text-white px-8 py-3 rounded-xl font-bold disabled:opacity-50">Próxima <ArrowRight size={18} className="inline" /></button>
                            </div>
                        </div>
                    )}

                    {isQuizFinished && !showAnswerKey && (
                        <div className="text-center py-8">
                            <Trophy size={64} className="mx-auto text-yellow-500 mb-6 animate-bounce" />
                            <h2 className="text-3xl font-bold text-slate-800 mb-2">Quiz Finalizado!</h2>
                            <p className="text-slate-500 mb-6 text-lg">Você acertou <span className="font-bold text-teal-600 text-2xl">{calculateScore()}</span> de {content.quiz.length}</p>
                            <p className={`font-medium text-xl mb-12 ${getMotivationMessage(calculateScore(), content.quiz.length).color}`}>{getMotivationMessage(calculateScore(), content.quiz.length).text}</p>
                            
                            <div className="grid gap-4 max-w-sm mx-auto">
                                <button 
                                    onClick={resetQuiz} 
                                    className="w-full bg-white border-2 border-slate-200 text-slate-700 px-6 py-4 rounded-xl font-bold hover:bg-slate-50 flex items-center justify-center gap-2"
                                >
                                    <RotateCcw size={20} /> Refazer Quiz
                                </button>
                                <button 
                                    onClick={() => setShowAnswerKey(true)} 
                                    className="w-full bg-slate-900 text-white px-6 py-4 rounded-xl font-bold shadow-lg hover:bg-slate-800 flex items-center justify-center gap-2"
                                >
                                    <Eye size={20} /> Revelar Gabarito
                                </button>
                            </div>
                        </div>
                    )}

                    {isQuizFinished && showAnswerKey && (
                         <div className="animate-in fade-in slide-in-from-bottom-4">
                             <div className="text-center mb-8">
                                <h2 className="text-2xl font-bold text-slate-800">Gabarito da Prova</h2>
                                <p className="text-slate-500">Confira abaixo onde você acertou e errou.</p>
                             </div>

                             <div className="space-y-6 mb-12">
                                {content.quiz.map((q, idx) => {
                                  const userAnswer = userAnswers[idx];
                                  const isCorrect = userAnswer === q.correctOptionIndex;
                                  return (
                                    <div key={idx} className={`p-6 rounded-xl border-2 ${isCorrect ? 'border-teal-100 bg-teal-50/30' : 'border-red-100 bg-red-50/30'}`}>
                                      <div className="flex gap-3">
                                        <div className={`mt-1 ${isCorrect ? 'text-teal-500' : 'text-red-500'}`}>{isCorrect ? <CheckCircle size={20} /> : <XCircle size={20} />}</div>
                                        <div>
                                          <h3 className="font-semibold text-slate-800 text-lg mb-2">{idx + 1}. {q.questionText}</h3>
                                          {!isCorrect && <p className="text-red-600 text-sm mb-1 flex items-center gap-1"><XCircle size={14} /> Sua resposta: <span className="font-bold">{q.options[userAnswer]}</span></p>}
                                          <p className="text-teal-700 text-sm font-medium flex items-center gap-1"><CheckCircle size={14} /> Resposta correta: <span className="font-bold">{q.options[q.correctOptionIndex]}</span></p>
                                        </div>
                                      </div>
                                    </div>
                                  );
                                })}
                             </div>

                             <div className="flex justify-center gap-4 border-t border-slate-100 pt-8">
                                <button onClick={resetQuiz} className="px-6 py-3 rounded-xl border border-slate-200 hover:bg-slate-50 font-semibold text-slate-700">Refazer Quiz</button>
                                <button onClick={() => setContent(null)} className="px-6 py-3 rounded-xl bg-teal-600 hover:bg-teal-700 text-white font-bold shadow-lg">Novo Assunto</button>
                            </div>
                         </div>
                    )}

                </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;