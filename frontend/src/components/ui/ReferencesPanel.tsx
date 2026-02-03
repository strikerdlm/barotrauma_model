/**
 * Scientific References Panel Component
 * 
 * Displays verifiable scientific citations supporting the model
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { scientificReferences, formatCitation, thresholdCitations, parameterSources } from '../../lib/references';
import { ChevronDown, ExternalLink, BookOpen, FlaskConical, AlertCircle } from 'lucide-react';

interface ReferencesPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

export const ReferencesPanel: React.FC<ReferencesPanelProps> = ({
  isOpen,
  onToggle,
}) => {
  const [activeSection, setActiveSection] = useState<'citations' | 'thresholds' | 'parameters'>('citations');

  return (
    <div className="card-glass">
      {/* Header */}
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 hover:bg-white/5 rounded-xl transition-colors"
      >
        <div className="flex items-center gap-3">
          <BookOpen className="w-5 h-5 text-primary-400" />
          <span className="font-display font-semibold text-white">Scientific References & Citations</span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <ChevronDown className="w-5 h-5 text-gray-400" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-4">
              {/* Section Tabs */}
              <div className="flex gap-2 border-b border-white/10 pb-2">
                {[
                  { id: 'citations', label: 'Publications', icon: <BookOpen className="w-4 h-4" /> },
                  { id: 'thresholds', label: 'Clinical Thresholds', icon: <AlertCircle className="w-4 h-4" /> },
                  { id: 'parameters', label: 'Model Parameters', icon: <FlaskConical className="w-4 h-4" /> },
                ].map((section) => (
                  <button
                    key={section.id}
                    onClick={() => setActiveSection(section.id as typeof activeSection)}
                    className={`
                      flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium
                      transition-colors duration-200
                      ${activeSection === section.id
                        ? 'bg-primary-500/20 text-primary-400'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                      }
                    `}
                  >
                    {section.icon}
                    {section.label}
                  </button>
                ))}
              </div>

              {/* Citations Section */}
              {activeSection === 'citations' && (
                <div className="space-y-3 max-h-[400px] overflow-y-auto pr-2">
                  {scientificReferences.map((ref) => (
                    <div
                      key={ref.id}
                      className="p-3 bg-dark-200/50 rounded-lg border border-white/5 hover:border-primary-500/30 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 space-y-1">
                          <p className="text-sm text-gray-300 leading-relaxed">
                            {formatCitation(ref)}
                          </p>
                          <p className="text-xs text-gray-500 italic">
                            {ref.relevance}
                          </p>
                        </div>
                        {ref.doi && (
                          <a
                            href={`https://doi.org/${ref.doi}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-primary-400 hover:text-primary-300 transition-colors"
                          >
                            <ExternalLink className="w-3 h-3" />
                            DOI
                          </a>
                        )}
                        {ref.pmid && (
                          <a
                            href={`https://pubmed.ncbi.nlm.nih.gov/${ref.pmid}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-xs text-purple-400 hover:text-purple-300 transition-colors"
                          >
                            <ExternalLink className="w-3 h-3" />
                            PubMed
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Thresholds Section */}
              {activeSection === 'thresholds' && (
                <div className="space-y-3">
                  {Object.entries(thresholdCitations).map(([key, threshold]) => (
                    <div
                      key={key}
                      className="p-3 bg-dark-200/50 rounded-lg border border-white/5"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-200">
                          {threshold.description}
                        </span>
                        <span className="font-mono text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded">
                          {threshold.value}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">{threshold.note}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Source: <span className="text-primary-500">{threshold.source}</span>
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Parameters Section */}
              {activeSection === 'parameters' && (
                <div className="space-y-3">
                  {Object.entries(parameterSources).map(([key, param]) => (
                    <div
                      key={key}
                      className="p-3 bg-dark-200/50 rounded-lg border border-white/5"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1">
                          <span className="text-sm font-medium text-gray-200 capitalize">
                            {key.replace(/([A-Z])/g, ' $1').trim()}
                          </span>
                          {'value' in param && (
                            <p className="font-mono text-sm text-primary-400 mt-1">
                              {param.value}
                            </p>
                          )}
                          {'formula' in param && (
                            <p className="font-mono text-sm text-purple-400 mt-1">
                              {param.formula}
                            </p>
                          )}
                          {'values' in param && (
                            <div className="mt-1 flex gap-2">
                              {Object.entries(param.values as Record<string, number>).map(([k, v]) => (
                                <span key={k} className="text-xs bg-dark-100 px-2 py-0.5 rounded">
                                  {k}: <span className="text-primary-400">{v}</span>
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">{param.note}</p>
                      <p className="text-xs text-gray-600">
                        Source: <span className="text-primary-500">{param.source}</span>
                      </p>
                    </div>
                  ))}
                </div>
              )}

              {/* Disclaimer */}
              <div className="p-3 bg-primary-500/10 border border-primary-500/20 rounded-lg">
                <p className="text-xs text-primary-300">
                  <strong>Note:</strong> All citations are verifiable through PubMed (PMID) or DOI links.
                  This model is based on peer-reviewed physiological research and is intended for
                  educational and research purposes. Clinical decisions should be made in consultation
                  with qualified medical professionals.
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ReferencesPanel;
