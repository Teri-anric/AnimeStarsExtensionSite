import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import ReactMarkdown from 'react-markdown';
import '../styles/FQAPage.css';

interface FAQSection {
  title: string;
  items: FAQItem[];
}

interface FAQItem {
  question: string;
  answer: string;
}

const FQAPage: React.FC = () => {
  const { t } = useTranslation();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionTitle: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionTitle)) {
      newExpanded.delete(sectionTitle);
    } else {
      newExpanded.add(sectionTitle);
    }
    setExpandedSections(newExpanded);
  };

  const faqData: FAQSection[] = [
    {
      title: t('fqa.extensionSetup.title'),
      items: [
        {
          question: t('fqa.extensionSetup.language.question'),
          answer: t('fqa.extensionSetup.language.answer')
        }
      ]
    },
    {
      title: t('fqa.automaticFunctions.title'),
      items: [
        {
          question: t('fqa.automaticFunctions.autoViewCards.question'),
          answer: t('fqa.automaticFunctions.autoViewCards.answer')
        },
        {
          question: t('fqa.automaticFunctions.collectCards.question'),
          answer: t('fqa.automaticFunctions.collectCards.answer')
        },
        {
          question: t('fqa.automaticFunctions.collectionAsWatchlist.question'),
          answer: t('fqa.automaticFunctions.collectionAsWatchlist.answer')
        },
        {
          question: t('fqa.automaticFunctions.addMyCardsButton.question'),
          answer: t('fqa.automaticFunctions.addMyCardsButton.answer')
        },
        {
          question: t('fqa.automaticFunctions.quickAccessButtons.question'),
          answer: t('fqa.automaticFunctions.quickAccessButtons.answer')
        },
        {
          question: t('fqa.automaticFunctions.autoTakeSkyStone.question'),
          answer: t('fqa.automaticFunctions.autoTakeSkyStone.answer')
        },
        {
          question: t('fqa.automaticFunctions.autoTakeCinemaStones.question'),
          answer: t('fqa.automaticFunctions.autoTakeCinemaStones.answer')
        }
      ]
    },
    {
      title: t('fqa.clubSettings.title'),
      items: [
        {
          question: t('fqa.clubSettings.highlightInTop.question'),
          answer: t('fqa.clubSettings.highlightInTop.answer')
        },
        {
          question: t('fqa.clubSettings.autoBoost.question'),
          answer: t('fqa.clubSettings.autoBoost.answer')
        },
        {
          question: t('fqa.clubSettings.refreshInterval.question'),
          answer: t('fqa.clubSettings.refreshInterval.answer')
        },
        {
          question: t('fqa.clubSettings.boostInterval.question'),
          answer: t('fqa.clubSettings.boostInterval.answer')
        }
      ]
    },
    {
      title: t('fqa.cardStatsSettings.title'),
      items: [
        {
          question: t('fqa.cardStatsSettings.showStats.question'),
          answer: t('fqa.cardStatsSettings.showStats.answer')
        },
        {
          question: t('fqa.cardStatsSettings.enableCaching.question'),
          answer: t('fqa.cardStatsSettings.enableCaching.answer')
        },
        {
          question: t('fqa.cardStatsSettings.parseUnlockedStats.question'),
          answer: t('fqa.cardStatsSettings.parseUnlockedStats.answer')
        },
        {
          question: t('fqa.cardStatsSettings.cacheLifetime.question'),
          answer: t('fqa.cardStatsSettings.cacheLifetime.answer')
        },
        {
          question: t('fqa.cardStatsSettings.requestDelay.question'),
          answer: t('fqa.cardStatsSettings.requestDelay.answer')
        },
        {
          question: t('fqa.cardStatsSettings.showEvent.question'),
          answer: t('fqa.cardStatsSettings.showEvent.answer')
        },
        {
          question: t('fqa.cardStatsSettings.templateEditor.question'),
          answer: t('fqa.cardStatsSettings.templateEditor.answer')
        }
      ]
    },
    {
      title: t('fqa.cardSearchSettings.title'),
      items: [
        {
          question: t('fqa.cardSearchSettings.integration.question'),
          answer: t('fqa.cardSearchSettings.integration.answer')
        }
      ]
    },
    {
      title: t('fqa.apiIntegration.title'),
      items: [
        {
          question: t('fqa.apiIntegration.sendStats.question'),
          answer: t('fqa.apiIntegration.sendStats.answer')
        },
        {
          question: t('fqa.apiIntegration.receiveStats.question'),
          answer: t('fqa.apiIntegration.receiveStats.answer')
        }
      ]
    },
    {
      title: t('fqa.updates.title'),
      items: [
        {
          question: t('fqa.updates.updateFlow.question'),
          answer: t('fqa.updates.updateFlow.answer')
        },
        {
          question: t('fqa.updates.disableUpdateCheck.question'),
          answer: t('fqa.updates.disableUpdateCheck.answer')
        }
      ]
    }
  ];

  return (
    <div className="fqa-page">
      <div className="fqa-container">
        <h1 className="fqa-title">{t('fqa.title')}</h1>
        <p className="fqa-description">{t('fqa.description')}</p>
        
        <div className="fqa-sections">
          {faqData.map((section, sectionIndex) => (
            <div key={sectionIndex} className="fqa-section">
              <button
                className={`fqa-section-header ${expandedSections.has(section.title) ? 'expanded' : ''}`}
                onClick={() => toggleSection(section.title)}
              >
                <span className="fqa-section-title">{section.title}</span>
                <span className="fqa-section-toggle">
                  {expandedSections.has(section.title) ? '−' : '+'}
                </span>
              </button>
              
              {expandedSections.has(section.title) && (
                <div className="fqa-section-content">
                  {section.items.map((item, itemIndex) => (
                    <div key={itemIndex} className="fqa-item">
                      <h3 className="fqa-question">{item.question}</h3>
                      <div className="fqa-answer">
                        <ReactMarkdown>{item.answer}</ReactMarkdown>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default FQAPage; 