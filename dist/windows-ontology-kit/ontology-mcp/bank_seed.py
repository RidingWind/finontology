"""银行业务本体种子定义 — 命令行脚本与 MCP server 共用的唯一真源。"""

from __future__ import annotations

import os

# (类名, 父类, 中文标签, 注释)
CLASSES = [
    ("BankParty", None, "参与方", "与银行发生业务往来或承担职责的自然人、法人与组织。"),
    ("Customer", "BankParty", "客户", "在银行开立账户、购买产品或接受服务的主体。"),
    ("PersonalCustomer", "Customer", "个人客户", "以自然人身份开户的客户，受个人身份识别与反洗钱核查约束。"),
    ("CorporateCustomer", "Customer", "对公客户", "以法人或非法人组织身份开户的客户，需核查受益所有人。"),
    ("InternalOrganization", "BankParty", "内部机构", "银行自身的组织单元，承担经营与管理职责。"),
    ("HeadOffice", "InternalOrganization", "总行", "承担全行管理、政策制定与集中运营职能的机构。"),
    ("Branch", "InternalOrganization", "分支机构", "在总行授权下开展属地经营活动的机构。"),
    ("Employee", "BankParty", "员工", "与银行建立劳动关系、行使系统权限的内部人员。"),
    ("ExternalPartner", "BankParty", "外部合作方", "与银行存在业务协作关系的第三方机构。"),

    ("FinancialProduct", None, "金融产品", "银行向客户提供的可销售金融服务单元。"),
    ("DepositProduct", "FinancialProduct", "存款产品", "以吸收存款为核心的产品，含活期、定期、大额存单等。"),
    ("LoanProduct", "FinancialProduct", "贷款产品", "以资金融出为核心的产品，含流动资金贷款、项目贷款、消费贷款等。"),
    ("WealthManagementProduct", "FinancialProduct", "理财产品", "受资管新规约束的代客理财与财富管理产品。"),
    ("SettlementService", "FinancialProduct", "支付结算服务", "为客户提供的资金收付与清算服务。"),
    ("IntermediaryBusiness", "FinancialProduct", "中间业务", "不构成表内资产负债、以手续费收入为主的业务。"),

    ("Contract", None, "合约", "银行与客户之间确立权利义务关系的法律文件与账户载体。"),
    ("Account", "Contract", "账户", "记录客户资金与产品持有状态的合约载体。"),
    ("DepositAccount", "Account", "存款账户", "承载存款产品的账户。"),
    ("LoanAccount", "Account", "贷款账户", "承载贷款产品额度与还款状态的账户。"),
    ("SettlementAccount", "Account", "结算账户", "用于资金收付与清算的账户。"),
    ("Agreement", "Contract", "协议", "约定服务条款与费用安排的书面或电子合约。"),

    ("FinancialTransaction", None, "金融交易", "引起资金或权利义务变动的业务事件。"),
    ("DepositTransaction", "FinancialTransaction", "存款交易", "资金存入账户的交易。"),
    ("WithdrawalTransaction", "FinancialTransaction", "取款交易", "资金从账户付出的交易。"),
    ("TransferTransaction", "FinancialTransaction", "转账交易", "账户之间资金转移的交易，至少涉及两个账户。"),
    ("PaymentTransaction", "FinancialTransaction", "支付交易", "向收款方完成资金支付义务的交易。"),
    ("ClearingTransaction", "FinancialTransaction", "清算交易", "机构之间完成资金与债权债务了结的交易。"),

    ("CashTransaction", "FinancialTransaction", "现金交易", "以实物现金收付完成的交易，需登记券别与柜员。"),
    ("CardTransaction", "FinancialTransaction", "银行卡交易", "通过银行卡介质发起的交易，涉及商户与受理终端。"),
    ("CardPurchaseTransaction", "CardTransaction", "卡消费交易", "持卡人在商户完成消费支付的交易。"),
    ("CardCashWithdrawalTransaction", "CardTransaction", "卡取现交易", "持卡人通过 ATM 或柜面提取现金的交易。"),
    ("CardRefundTransaction", "CardTransaction", "卡退货交易", "对已发生消费交易的全部或部分冲正退款。"),
    ("ForeignExchangeTransaction", "FinancialTransaction", "外汇买卖交易", "两种币种之间按汇率兑换的交易。"),
    ("FXSpotTransaction", "ForeignExchangeTransaction", "即期外汇交易", "成交后两个工作日内完成交割的外汇买卖。"),
    ("FXForwardTransaction", "ForeignExchangeTransaction", "远期外汇交易", "约定未来日期与汇率交割的外汇买卖。"),
    ("FXSwapTransaction", "ForeignExchangeTransaction", "外汇掉期交易", "两笔币种相同、方向相反、交割日不同的外汇买卖组合。"),
    ("BillTransaction", "FinancialTransaction", "票据交易", "围绕票据权利义务变动办理的交易。"),
    ("BillAcceptanceTransaction", "BillTransaction", "票据承兑交易", "承兑人承诺到期付款的票据行为。"),
    ("BillDiscountTransaction", "BillTransaction", "票据贴现交易", "持票人将未到期票据转让给银行换取资金。"),
    ("BillRediscountTransaction", "BillTransaction", "转贴现与再贴现交易", "银行间转让票据或向央行贴现的交易。"),
    ("BillSettlementTransaction", "BillTransaction", "票据到期付款交易", "票据到期时由承兑人完成付款了结。"),
    ("InvestmentTransaction", "FinancialTransaction", "投资理财交易", "围绕理财产品与投资品种的认购与赎回交易。"),
    ("WealthSubscriptionTransaction", "InvestmentTransaction", "理财认购交易", "客户申购理财产品份额的交易。"),
    ("WealthRedemptionTransaction", "InvestmentTransaction", "理财赎回交易", "客户赎回理财产品份额的交易。"),
    ("FeeTransaction", "FinancialTransaction", "收费与计息交易", "因服务收费或资金计息引发的资金变动。"),
    ("FeeChargeTransaction", "FeeTransaction", "手续费收取交易", "按价目表收取服务费用的交易。"),
    ("InterestSettlementTransaction", "FeeTransaction", "利息结算交易", "存款结息或贷款收息的资金结算。"),
    ("CrossBorderTransaction", "FinancialTransaction", "跨境交易", "资金跨越国境收付的交易，须履行国际收支申报与制裁筛查。"),
    ("InwardRemittanceTransaction", "CrossBorderTransaction", "汇入汇款交易", "资金由境外汇入境内的汇款交易。"),
    ("OutwardRemittanceTransaction", "CrossBorderTransaction", "汇出汇款交易", "资金由境内汇往境外的汇款交易。"),
    ("AgencyTransaction", "FinancialTransaction", "代收付与批量交易", "受委托单位委托批量办理的收付款交易。"),
    ("AgencyCollectionTransaction", "AgencyTransaction", "委托代收交易", "受委托向付款方收取款项的交易。"),
    ("AgencyPaymentTransaction", "AgencyTransaction", "委托代付交易", "受委托向收款方支付款项的交易。"),
    ("BatchDebitTransaction", "AgencyTransaction", "批量代扣交易", "按委托协议批量从多个账户扣收款项。"),
    ("BatchCreditTransaction", "AgencyTransaction", "批量代发交易", "按委托协议批量向多个账户发放款项。"),

    ("AgencyAgreement", "Agreement", "委托代收付协议", "银行与委托单位约定批量收付款权利义务的协议。"),
    ("CorrespondentBank", "ExternalPartner", "代理行", "为本行跨境清算提供账户与通道服务的境外同业机构。"),

    ("ServiceChannel", None, "服务渠道", "客户触达银行服务的通路。"),
    ("CounterChannel", "ServiceChannel", "柜面渠道", "通过网点柜员人工办理业务的渠道。"),
    ("InternetBankingChannel", "ServiceChannel", "网上银行渠道", "通过浏览器访问的电子银行渠道。"),
    ("MobileBankingChannel", "ServiceChannel", "手机银行渠道", "通过移动端应用访问的电子银行渠道。"),
    ("SelfServiceChannel", "ServiceChannel", "自助渠道", "自助终端与智能柜台等无人值守渠道。"),
    ("OpenApiChannel", "ServiceChannel", "开放银行API渠道", "通过标准化接口向合作方开放能力的渠道。"),

    ("RiskAndCompliance", None, "风险与合规", "风险控制与合规管理领域的对象集合。"),
    ("RiskEvent", "RiskAndCompliance", "风险事件", "已识别或已发生的信用、市场、操作、流动性等风险事件。"),
    ("ComplianceRequirement", "RiskAndCompliance", "合规要求", "法律法规、监管规定与内部制度提出的约束性要求。"),
    ("RegulatoryReport", "RiskAndCompliance", "监管报送", "按监管口径定期或不定期报送的数据与报表。"),
    ("AuditRecord", "RiskAndCompliance", "审计记录", "记录关键操作与审批轨迹、不可抵赖的留痕数据。"),

    ("SecurityDomain", None, "安全域", "身份、权限与密码学相关的安全对象集合。"),
    ("Role", "SecurityDomain", "角色", "权限分配的逻辑集合，是 RBAC 授权模型的核心。"),
    ("SystemAdministrationRole", "Role", "系统管理权角色", "掌握系统配置、参数与账号管理权限的角色。"),
    ("BusinessOperationRole", "Role", "业务操作权角色", "掌握业务办理与交易操作权限的角色。"),
    ("AuditRole", "Role", "审计权角色", "掌握日志审计与行为追溯权限的角色。"),
    ("SupervisionRole", "Role", "监督权角色", "掌握合规监督与风险监控权限的角色。"),
    ("Permission", "SecurityDomain", "权限", "对系统功能或数据对象的具体操作许可。"),
    ("CryptographicKey", "SecurityDomain", "密钥", "用于加密、签名与完整性保护的密钥材料。"),
    ("CryptoAlgorithm", "SecurityDomain", "密码算法", "实现机密性、完整性与不可否认性的算法。"),
    ("SymmetricAlgorithm", "CryptoAlgorithm", "对称算法", "加解密使用相同密钥的算法，如 SM4、AES。"),
    ("AsymmetricAlgorithm", "CryptoAlgorithm", "非对称算法", "使用公私钥对的算法，如 SM2、RSA。"),
    ("HashAlgorithm", "CryptoAlgorithm", "摘要算法", "生成定长摘要用于完整性校验的算法，如 SM3。"),
    ("SecurityPolicy", "SecurityDomain", "安全策略", "约束系统行为的成文安全规则集合。"),

    ("TechnicalComponent", None, "技术组件", "支撑业务运行的基础技术设施与公共服务。"),
    ("CryptoService", "TechnicalComponent", "加密服务", "提供密钥管理与密码运算的统一服务。"),
    ("FileTransferService", "TechnicalComponent", "文件传输服务", "提供跨系统可靠文件交换的服务。"),
    ("MessageQueue", "TechnicalComponent", "消息中间件", "提供异步解耦与可靠投递的消息服务。"),
    ("LoggingService", "TechnicalComponent", "日志服务", "统一采集与留存系统运行与操作日志。"),
    ("MonitoringService", "TechnicalComponent", "监控服务", "采集指标、告警与健康状况的服务。"),
    ("SchedulingService", "TechnicalComponent", "调度服务", "统一编排批处理与定时任务的服务。"),

    ("DataAsset", None, "数据资产", "银行经营过程中产生与沉淀的数据对象。"),
    ("DataEntity", "DataAsset", "数据实体", "经过建模的业务数据对象，构成数据模型的基本单元。"),
    ("DataSet", "DataAsset", "数据集", "面向特定用途组织的数据实体集合。"),
    ("BusinessMetric", "DataAsset", "业务指标", "口径明确、可度量的经营与管理指标。"),

    ("RegulatoryBody", "ExternalPartner", "监管机构", "依法对银行实施监督管理职能的机构。"),
    ("ReportingStatus", "RiskAndCompliance", "报送状态", "监管报送所处的生命周期状态。"),
    ("ReportingBatch", "RiskAndCompliance", "报送批次", "同一报送任务下一次性提交的一组报文。"),
    ("ReportingTask", "RiskAndCompliance", "报送任务", "按监管要求组织报文编制、复核与提交的工作单元。"),
    ("ReportingDataItem", "DataEntity", "报送数据项", "监管口径下明确定义的最小报送字段。"),
    ("ReportingRule", "ComplianceRequirement", "报送校验规则", "报文须满足的口径、勾稽与校验约束。"),

    ("EASTReport", "RegulatoryReport", "EAST 报送", "监管数据标准化报送，覆盖表内外业务明细数据。"),
    ("StatutoryReport1104", "RegulatoryReport", "1104 非现场监管报表", "向金融监管部门报送的非现场监管报表系列。"),
    ("AMLReport", "RegulatoryReport", "反洗钱报送", "大额交易与可疑交易等反洗钱报送。"),
    ("CreditRegistryReport", "RegulatoryReport", "征信报送", "向征信系统报送的客户信贷信息。"),
    ("FinancialStatisticsReport", "RegulatoryReport", "金融统计报送", "向人民银行报送的全科目金融统计报表。"),
    ("PaymentSettlementReport", "RegulatoryReport", "支付结算报表", "支付结算业务相关的监管报表。"),

    ("CreditRiskEvent", "RiskEvent", "信用风险事件", "因交易对手违约或信用质量下降引发的风险事件。"),
    ("MarketRiskEvent", "RiskEvent", "市场风险事件", "因市场价格不利变动引发的风险事件。"),
    ("OperationalRiskEvent", "RiskEvent", "操作风险事件", "因内部流程、人员、系统缺陷或外部事件引发的风险事件。"),
    ("LiquidityRiskEvent", "RiskEvent", "流动性风险事件", "因资金错配或融资能力不足引发的风险事件。"),
    ("ComplianceRiskEvent", "RiskEvent", "合规风险事件", "因违反法律法规或监管规定引发的风险事件。"),

    ("EASTDataItem", "ReportingDataItem", "EAST 数据项", "监管数据标准化（EAST）报送口径下的数据项。"),
    ("EASTCustomerItem", "EASTDataItem", "客户主题域数据项", "EAST 客户信息主题的报送字段集合。"),
    ("EASTAccountItem", "EASTDataItem", "账户主题域数据项", "EAST 账户信息主题的报送字段集合。"),
    ("EASTDepositItem", "EASTDataItem", "存款主题域数据项", "EAST 存款业务主题的报送字段集合。"),
    ("EASTLoanItem", "EASTDataItem", "贷款主题域数据项", "EAST 信贷管理主题的报送字段集合。"),
    ("EASTTransactionItem", "EASTDataItem", "交易主题域数据项", "EAST 交易流水主题的报送字段集合。"),

    ("EASTBillItem", "EASTDataItem", "票据主题域数据项", "EAST 票据业务主题的报送字段集合，覆盖承兑、贴现、转贴现与再贴现。"),
    ("EASTInterbankItem", "EASTDataItem", "同业主题域数据项", "EAST 同业业务主题的报送字段集合，覆盖拆借、存放、买入返售与同业存单。"),
    ("EASTWealthItem", "EASTDataItem", "理财主题域数据项", "EAST 理财业务主题的报送字段集合，覆盖产品募集、净值与客户持有。"),
    ("EASTOffBalanceItem", "EASTDataItem", "表外主题域数据项", "EAST 表外业务主题的报送字段集合，覆盖保函、信用证、承诺与衍生品。"),

    ("Bill", "Contract", "票据", "以无条件支付确定金额为标的的有价凭证。"),
    ("BankAcceptanceBill", "Bill", "银行承兑汇票", "由银行承担到期付款责任的汇票，同时构成表外承兑承担。"),
    ("CommercialAcceptanceBill", "Bill", "商业承兑汇票", "由银行以外的付款人承兑的汇票。"),
    ("InterbankBusiness", "Contract", "同业业务", "银行与其他金融机构之间开展资金融通与往来的业务合约。"),
    ("InterbankLending", "InterbankBusiness", "同业拆借", "金融机构之间的短期无担保资金融通。"),
    ("InterbankDeposit", "InterbankBusiness", "同业存放", "金融机构之间以存放形式开展的资金往来。"),
    ("ReverseRepo", "InterbankBusiness", "买入返售", "以买入并约定返售方式开展的资金融出业务。"),
    ("InterbankCD", "InterbankBusiness", "同业存单", "存款类金融机构发行的记账式定期存款凭证。"),
    ("OffBalanceCommitment", "Contract", "表外承担", "不列入资产负债表但形成或有权利义务的业务。"),
    ("Guarantee", "OffBalanceCommitment", "保函", "银行应申请人要求向受益人出具的付款保证。"),
    ("LetterOfCredit", "OffBalanceCommitment", "信用证", "银行依申请开立的有条件付款承诺凭证。"),
    ("AcceptanceCommitment", "OffBalanceCommitment", "承兑承诺", "银行对汇票承兑所形成的或有付款义务。"),
    ("CreditCommitment", "OffBalanceCommitment", "贷款承诺", "银行承诺在未来按约定条件提供信贷的安排。"),
    ("DerivativeContract", "OffBalanceCommitment", "衍生品合约", "价值依附于基础资产或指数的金融合约。"),

    ("SeparationOfDutyViolation", "RiskAndCompliance", "职责分离违规", "由 SWRL 规则推导得出：同一主体被赋予存在职责分离约束的两个角色，或同时承担互斥的岗位职责。SWRL 是单调的，只能标记不能阻止，真正的强制须在 RBAC 授权服务层实现。"),

    ("DemandDepositProduct", "DepositProduct", "活期存款产品", "无固定期限、可随时存取的存款产品。"),
    ("TimeDepositProduct", "DepositProduct", "定期存款产品", "约定存期与利率、到期支取的存款产品。"),
    ("LargeCDProduct", "DepositProduct", "大额存单产品", "面向特定对象发行、可转让的标准化定期存款凭证。"),

    ("WorkingCapitalLoanProduct", "LoanProduct", "流动资金贷款", "满足企业日常经营周转需要的贷款产品。"),
    ("ProjectLoanProduct", "LoanProduct", "项目贷款", "针对特定建设项目发放、以项目收益偿还的贷款产品。"),
    ("ConsumerLoanProduct", "LoanProduct", "消费贷款", "面向个人消费用途发放的贷款产品。"),
    ("MortgageLoanProduct", "LoanProduct", "按揭贷款", "以所购资产抵押、分期偿还的贷款产品。"),

    ("AgencyBusiness", "IntermediaryBusiness", "代理业务", "代客户办理收付、代销等代理类中间业务。"),
    ("GuaranteeBusiness", "IntermediaryBusiness", "担保类中间业务", "以银行信用提供担保并收取手续费的中间业务。"),
    ("CommitmentBusiness", "IntermediaryBusiness", "承诺类中间业务", "形成或有债权债务承诺的中间业务。"),
    ("TradingAgencyBusiness", "IntermediaryBusiness", "交易类中间业务", "代理客户进行金融工具交易的中间业务。"),

    ("Collateral", None, "押品", "为担保债权实现而设定担保权利的财产或权利。"),
    ("CashCollateral", "Collateral", "现金类押品", "保证金、存单等现金及现金等价物形态的押品。"),
    ("RealEstateCollateral", "Collateral", "不动产押品", "土地使用权、房屋建筑物等不动产形态的押品。"),
    ("ReceivablesCollateral", "Collateral", "应收账款押品", "以应收账款债权设定的押品。"),
    ("SecuritiesCollateral", "Collateral", "有价证券押品", "以股票、债券、基金份额等有价证券设定的押品。"),
    ("MovableCollateral", "Collateral", "动产押品", "机器设备、存货、车辆等动产形态的押品。"),

    ("BeneficialOwner", "BankParty", "受益所有人", "最终有效控制或享有法人客户收益的自然人，反洗钱与客户尽职调查的核查对象。"),

    ("CreditRating", "RiskAndCompliance", "信用评级", "对客户或债项偿债能力与违约风险的评价结果。"),
    ("RiskIndicator", "RiskAndCompliance", "风险指标", "用于量化监测与预警风险水平的计量指标。"),
    ("CreditLimit", "RiskAndCompliance", "授信额度", "银行核定的客户可使用的信用敞口上限。"),

    ("UserAccount", "SecurityDomain", "系统账号", "员工在信息系统中用于身份鉴别与访问控制的账号凭证。"),

    ("DatabaseService", "TechnicalComponent", "数据库服务", "提供数据持久化存储与访问的组件。"),
    ("APIGateway", "TechnicalComponent", "API 网关", "统一对外暴露服务接口并提供鉴权、限流与路由的组件。"),
    ("CacheService", "TechnicalComponent", "缓存服务", "提供高速数据访问以承载热点读写的组件。"),
    ("ConfigCenter", "TechnicalComponent", "配置中心", "集中管理与下发系统配置参数的组件。"),

    ("DataStandard", "DataAsset", "数据标准", "对数据定义、口径与编码规则的统一约定。"),
    ("DataModel", "DataAsset", "数据模型", "对数据结构、关系与约束的抽象描述。"),
    ("DataQualityRule", "ComplianceRequirement", "数据质量规则", "数据须满足的准确性、完整性与一致性约束。"),

    # --- 映射元数据域（报送字段 ↔ 本体属性 ↔ 源表字段 三元关系的载体）---
    # 设计要点：报送字段在本体中是「数据属性」而非实例，无法作为对象属性的客体，
    # 因此 FieldMapping 用数据属性 targetOntologyProperty 以名称引用目标属性。
    ("MappingMetadata", "DataAsset", "映射元数据", "描述报送口径、本体属性与源系统字段之间对应关系的元数据总称。"),
    ("MappingSpecification", "MappingMetadata", "映射规格", "某一报送口径下一组字段映射条目的集合，按版本管理。"),
    ("FieldMapping", "MappingMetadata", "字段映射条目", "三元关系的核心载体：一条报送字段与源表字段（或转换逻辑）的对应关系。"),
    ("SourceTable", "MappingMetadata", "源系统表", "源业务系统中承载报送数据的数据表。"),
    ("SourceField", "MappingMetadata", "源表字段", "源系统表中的具体字段。"),
    ("TransformationRule", "MappingMetadata", "转换规则", "源值到报送值之间的加工逻辑定义。"),
    ("CodeMapping", "MappingMetadata", "代码转换表", "源系统代码值与监管口径代码值的对照条目。"),
    ("MappingCoverage", "MappingMetadata", "映射覆盖率快照", "某时点映射完备程度的度量结果，供校验与追踪。"),

    # --- 机构层级与岗位 ---
    ("SubBranch", "Branch", "支行", "隶属于分行、直接面向客户经营的机构。"),
    ("Outlet", "SubBranch", "营业网点", "对外办理柜面业务的物理场所。"),
    ("Department", "InternalOrganization", "内设部门", "机构内部按职能划分的组织单元，如公司金融部、风险管理部。"),
    ("Position", "BankParty", "岗位", "组织内承担特定职责与权限的位置，是 RBAC 赋权与职责分离的载体。"),

    # --- 会计账务域（新增顶层域）---
    ("Accounting", None, "会计账务域", "以复式记账为基础记录、归集与反映银行经济事项的领域。"),
    ("AccountingSubject", "Accounting", "会计科目", "对会计要素进行分类核算的科目，是账务处理的基础。"),
    ("AssetSubject", "AccountingSubject", "资产类科目", "反映银行拥有或控制的资源的科目。"),
    ("LiabilitySubject", "AccountingSubject", "负债类科目", "反映银行所承担债务的科目。"),
    ("EquitySubject", "AccountingSubject", "所有者权益类科目", "反映所有者对净资产享有权益的科目。"),
    ("IncomeSubject", "AccountingSubject", "损益类收入科目", "反映经营成果中收入部分的科目。"),
    ("ExpenseSubject", "AccountingSubject", "损益类支出科目", "反映经营成果中支出部分的科目。"),
    ("OffBalanceSubject", "AccountingSubject", "表外科目", "核算不在资产负债表内反映但需登记的或有事项科目。刻意不参与科目互斥——表外事项可能同时具备或有资产与或有负债性质。"),
    ("AccountingVoucher", "Accounting", "记账凭证", "载明经济事项并据以登记账簿的书面记录。"),
    ("AccountingEntry", "Accounting", "会计分录", "按复式记账规则记录一笔经济事项借贷双方的账务单元。"),
    ("Ledger", "Accounting", "账簿", "按既定口径登记账务记录的簿籍，是总账与分户账的共同父类。"),
    ("GeneralLedger", "Ledger", "总账", "按会计科目汇总登记的账簿。"),
    ("SubLedger", "Ledger", "分户账", "按账户或客户明细登记的账簿，与总账勾稽。"),
    ("AccountingPeriod", "Accounting", "会计期间", "进行账务核算与结账的时间区间。"),

    # --- 担保与保证 ---
    ("Guarantor", "BankParty", "担保人", "为债务人履行债务提供担保的自然人或法人。"),
    ("CorporateGuarantor", "Guarantor", "法人担保人", "以法人或非法人组织身份提供担保的主体。"),
    ("PersonalGuarantor", "Guarantor", "自然人担保人", "以自然人身份提供担保的主体。"),
    ("GuaranteeContract", "Agreement", "担保合同", "约定担保权利义务的从合同，依附于主债权合同。"),
    ("SuretyshipContract", "GuaranteeContract", "保证合同", "以保证人信用提供担保的合同，不涉及特定押品。"),
    ("MortgageContract", "GuaranteeContract", "抵押合同", "以不动产等抵押物提供担保的合同，抵押物不转移占有。"),
    ("PledgeContract", "GuaranteeContract", "质押合同", "以动产或权利凭证提供担保的合同，质押物转移占有。"),

    # --- 定价与利率（新增顶层域）---
    ("PricingDomain", None, "定价域", "金额、利率与费用的确定规则与计量口径。"),
    ("InterestRate", "PricingDomain", "利率", "资金使用的价格，按期限、币种与计息方式确定。"),
    ("BenchmarkRate", "InterestRate", "基准利率", "由市场或官方公布的参考利率，如 LPR、Shibor。"),
    ("ExecutingRate", "InterestRate", "执行利率", "在基准利率基础上加减点后实际适用于具体业务的利率。"),
    ("FeeItem", "PricingDomain", "收费项目", "对特定服务收取费用的项目定义。"),
    ("FeeSchedule", "PricingDomain", "价目表", "按版本管理的收费项目与费率集合。"),

    # --- 反洗钱与尽职调查 ---
    ("CustomerRiskLevel", "RiskAndCompliance", "客户风险等级", "反洗钱口径下对客户洗钱与恐怖融资风险的评级结果。"),
    ("DueDiligence", "RiskAndCompliance", "尽职调查", "为客户身份识别与风险评估所开展的核查活动。"),
    ("SimplifiedDueDiligence", "DueDiligence", "简化尽职调查", "对低风险客户采取的简化核查措施。"),
    ("StandardDueDiligence", "DueDiligence", "标准尽职调查", "对一般风险客户采取的常规核查措施。"),
    ("EnhancedDueDiligence", "DueDiligence", "加强尽职调查", "对高风险客户、政要或高风险地域采取的强化核查措施。"),
    ("SuspiciousTransactionReport", "RiskAndCompliance", "可疑交易报告", "发现可疑情形后向反洗钱监测中心报送的报告。"),
    ("LargeAmountTransactionReport", "RiskAndCompliance", "大额交易报告", "达到规定金额门槛后报送的交易报告。"),
    ("SanctionsScreening", "RiskAndCompliance", "制裁名单筛查", "对客户或交易对手开展制裁与恐怖分子名单的比对筛查。"),

    # --- 资本计量与风险缓释 ---
    ("Exposure", "RiskAndCompliance", "风险敞口", "在不利事件下可能承受损失的暴露金额。"),
    ("CreditExposure", "Exposure", "信用风险敞口", "因交易对手违约可能形成的风险暴露。"),
    ("MarketExposure", "Exposure", "市场风险敞口", "因市场价格不利变动可能形成的风险暴露。"),
    ("OperationalExposure", "Exposure", "操作风险敞口", "因内部流程、人员或系统缺陷可能形成的风险暴露。"),
    ("RiskWeightedAsset", "RiskAndCompliance", "风险加权资产", "按风险权重折算后的资产额，是资本充足率的分母。"),
    ("Provision", "RiskAndCompliance", "拨备", "为抵补预期损失而计提的准备金。"),
    ("LoanLossProvision", "Provision", "贷款损失准备", "针对贷款资产计提的损失准备金。"),
    ("Impairment", "RiskAndCompliance", "减值", "按预期信用损失模型确认的资产价值减损。"),
    ("CapitalAdequacy", "RiskAndCompliance", "资本充足率计量", "资本与风险加权资产的比率测算，含各级资本构成。"),
    ("RiskMitigation", "RiskAndCompliance", "风险缓释", "通过押品、保证或净额结算等手段降低风险暴露的安排。"),

    # --- 运营与清算（新增顶层域）---
    ("BankOperation", None, "运营域", "支撑账务处理、清算与日常运行的作业活动。"),
    ("BatchJob", "BankOperation", "批处理作业", "按计划批量执行的作业，如日终结息、批量代扣、报表加工。"),
    ("Reconciliation", "BankOperation", "对账", "两个或多个账务记录之间的核对作业，用于发现差异。"),
    ("OperationalError", "BankOperation", "运营差错", "业务处理过程中发生的需更正的错误记录。"),
    ("SettlementSession", "BankOperation", "清算场次", "支付系统在规定时点集中完成资金了结的场次。"),
]

# (属性名, 定义域, 值域, 特性, 逆属性, 中文标签, 注释)
OBJECT_PROPERTIES = [
    ("holdsAccount", ["BankParty"], ["Account"], [], None, "持有账户", "参与方对账户的持有关系。"),
    ("signsAgreement", ["BankParty"], ["Agreement"], [], None, "签署协议", "参与方签署协议的行为关系。"),
    ("appliesProduct", ["Account"], ["FinancialProduct"], [], None, "适用产品", "账户所承载的金融产品。"),
    ("initiatesTransaction", ["BankParty"], ["FinancialTransaction"], [], None, "发起交易", "参与方主动发起的交易。"),
    ("viaChannel", ["FinancialTransaction"], ["ServiceChannel"], [], None, "经由渠道", "交易所使用的服务渠道。"),
    ("involvesAccount", ["FinancialTransaction"], ["Account"], [], None, "涉及账户", "交易所影响的账户。"),
    ("belongsToOrganization", ["Employee"], ["InternalOrganization"], ["functional"], None, "隶属机构", "员工所属的内部机构。"),
    ("assignedRole", ["BankParty"], ["Role"], [], None, "被授予角色", "参与方被分配的角色。"),
    ("grantsPermission", ["Role"], ["Permission"], [], None, "授予权限", "角色所包含的权限。"),
    ("separatedFrom", ["Role"], ["Role"], ["symmetric"], None, "职责分离于", "四权分离约束：两个角色不得由同一主体同时持有。"),
    ("hasRiskEvent", ["FinancialTransaction"], ["RiskEvent"], [], None, "产生风险事件", "交易触发或关联的风险事件。"),
    ("governedBy", ["FinancialTransaction", "Account", "TechnicalComponent"], ["ComplianceRequirement"], [], None, "受合规约束", "对象须遵循的合规要求。"),
    ("generatesAuditRecord", ["FinancialTransaction"], ["AuditRecord"], [], None, "生成审计记录", "交易产生的不可抵赖审计留痕。"),
    ("signedWith", ["AuditRecord"], ["CryptoAlgorithm"], [], None, "签名算法", "审计记录所使用的签名算法，满足 AC-9.3 要求。"),
    ("protectedBy", ["DataAsset", "FinancialTransaction"], ["CryptoAlgorithm"], [], None, "受算法保护", "对象所受的密码算法保护。"),
    ("usesKey", ["CryptoAlgorithm"], ["CryptographicKey"], [], None, "使用密钥", "算法运行所依赖的密钥材料。"),
    ("dependsOnComponent", ["TechnicalComponent"], ["TechnicalComponent"], ["transitive"], None, "依赖组件", "技术组件之间的依赖，具备传递性。"),
    ("derivedFrom", ["DataSet"], ["DataEntity"], [], None, "源自实体", "数据集的数据来源实体。"),
    ("producesMetric", ["DataSet"], ["BusinessMetric"], [], None, "产出指标", "数据集计算得出的业务指标。"),

    ("submittedBy", ["RegulatoryReport"], ["InternalOrganization"], [], None, "报送主体", "提交报文的内部机构。"),
    ("submittedTo", ["RegulatoryReport"], ["RegulatoryBody"], [], None, "报送对象", "报文提交的目标监管机构。"),
    ("hasDataItem", ["RegulatoryReport"], ["ReportingDataItem"], [], None, "包含数据项", "报文所包含的监管数据项。"),
    ("governedByRule", ["ReportingDataItem"], ["ReportingRule"], [], None, "受校验规则约束", "数据项须满足的校验规则。"),
    ("inBatch", ["RegulatoryReport"], ["ReportingBatch"], ["functional"], None, "所属批次", "报文所属的报送批次。"),
    ("hasStatus", ["RegulatoryReport"], ["ReportingStatus"], ["functional"], None, "报送状态", "报文当前所处的生命周期状态。"),
    ("producedFrom", ["RegulatoryReport"], ["DataSet"], [], None, "产出自数据集", "报文数据的来源数据集。"),
    ("reviewsReport", ["Employee"], ["RegulatoryReport"], [], None, "复核报文", "复核报文的员工，须与编制人职责分离。"),
    ("compilesReport", ["Employee"], ["RegulatoryReport"], [], None, "编制报文", "编制报文的员工，须与复核人职责分离。"),
    ("containsReport", ["ReportingBatch"], ["RegulatoryReport"], [], None, "包含报文", "批次所包含的报文。"),

    ("involvesBill", ["BillTransaction"], ["Bill"], [], None, "涉及票据", "票据交易所指向的票据凭证。"),
    ("involvesInvestmentProduct", ["InvestmentTransaction"], ["WealthManagementProduct"], [], None, "涉及投资产品", "投资理财交易所认购或赎回的产品。"),
    ("underAgreement", ["AgencyTransaction"], ["AgencyAgreement"], ["functional"], None, "依据委托协议", "代收付交易所依据的委托协议。"),
    ("viaCorrespondentBank", ["CrossBorderTransaction"], ["CorrespondentBank"], [], None, "经由代理行", "跨境交易所借用的境外代理行通道。"),
    ("reportsEntity", [], [], ["functional"], None, "报送源实体", "报送记录所指向的业务实体。刻意不设 rdfs:domain 与 rdfs:range——多值 domain/range 在 OWL 中是交集语义，九个主题域各指向不同实体类型，改由各主题域的 ∃ 限制公理分别表达。"),

    ("securedBy", ["LoanAccount"], ["Collateral"], [], None, "由押品担保", "贷款债权由押品提供担保，信用贷款无此关系。"),
    ("hasBeneficialOwner", ["CorporateCustomer"], ["BeneficialOwner"], [], None, "受益所有人", "对公客户的最终受益自然人，反洗钱尽职调查的核查对象。"),
    ("hasCreditRating", ["Customer"], ["CreditRating"], [], None, "信用评级", "客户所获得的信用评级结果。"),
    ("hasCreditLimit", ["Customer"], ["CreditLimit"], [], None, "授信额度", "客户获核定的可使用信用敞口上限。"),
    ("measuredBy", ["RiskEvent"], ["RiskIndicator"], [], None, "由指标度量", "风险事件由风险指标量化反映。"),
    ("hasUserAccount", ["Employee"], ["UserAccount"], [], None, "持有系统账号", "员工在信息系统中的账号，是 RBAC 赋权的实际载体。"),
    ("holdsProduct", ["Customer"], ["FinancialProduct"], [], None, "持有产品", "客户持有或购买的金融产品。"),
    ("conformsToStandard", ["DataEntity"], ["DataStandard"], [], None, "遵循数据标准", "数据实体所遵循的数据标准。"),
    ("belongsToModel", ["DataEntity"], ["DataModel"], [], None, "所属数据模型", "数据实体所属的数据模型。"),
    ("governedByQualityRule", ["DataEntity"], ["DataQualityRule"], [], None, "受质量规则约束", "数据实体须满足的数据质量规则。"),

    # --- 映射元数据域对象属性 ---
    ("hasFieldMapping", ["MappingSpecification"], ["FieldMapping"], [], None, "包含映射条目", "映射规格所包含的字段映射条目。"),
    ("inSpecification", ["FieldMapping"], ["MappingSpecification"], ["functional"], None, "所属映射规格", "字段映射条目所归属的映射规格。"),
    ("mapsSourceField", ["FieldMapping"], ["SourceField"], ["functional"], None, "映射源字段", "映射条目所取数的源表字段；未映射时可缺省。"),
    ("hasSourceField", ["SourceTable"], ["SourceField"], [], None, "包含字段", "源系统表所包含的字段。"),
    ("belongsToTable", ["SourceField"], ["SourceTable"], ["functional"], None, "所属源表", "源字段所属的数据表。"),
    ("usesTransformationRule", ["FieldMapping"], ["TransformationRule"], [], None, "采用转换规则", "映射条目所采用的加工逻辑。"),
    ("usesCodeMapping", ["FieldMapping"], ["CodeMapping"], [], None, "采用代码对照", "映射条目所引用的代码转换条目。"),
    ("hasCoverage", ["MappingSpecification"], ["MappingCoverage"], [], None, "覆盖率快照", "映射规格在某一时点的覆盖率度量结果。"),

    # --- 机构层级与岗位 ---
    ("subOrganizationOf", ["InternalOrganization"], ["InternalOrganization"], ["functional"], None,
     "上级机构", "机构在组织层级中的直接上级。"),
    ("holdsPosition", ["Employee"], ["Position"], [], None, "担任岗位", "员工所担任的岗位，可兼任多个。"),
    ("positionRequiresRole", ["Position"], ["Role"], [], None, "岗位所需角色", "履行岗位职能所需的系统角色，是 RBAC 赋权的依据。"),

    # --- 会计账务域 ---
    ("debitSubject", ["AccountingEntry"], ["AccountingSubject"], ["functional"], None,
     "借方科目", "分录中记入借方的会计科目。"),
    ("creditSubject", ["AccountingEntry"], ["AccountingSubject"], ["functional"], None,
     "贷方科目", "分录中记入贷方的会计科目。"),
    ("inVoucher", ["AccountingEntry"], ["AccountingVoucher"], ["functional"], None,
     "所属凭证", "分录所属的记账凭证。"),
    ("inPeriod", ["AccountingVoucher"], ["AccountingPeriod"], ["functional"], None,
     "所属会计期间", "凭证记账所归属的会计期间。"),
    ("affectsAccount", ["AccountingEntry"], ["Account"], [], None, "影响账户", "分录所影响的账户。"),
    ("ledgerOfAccount", ["SubLedger"], ["Account"], ["functional"], None, "分户账对应账户", "分户账所登记明细的账户。"),
    ("subjectOfLedger", ["GeneralLedger"], ["AccountingSubject"], ["functional"], None, "总账科目", "总账所归集的会计科目。"),

    # --- 担保与保证 ---
    ("guaranteedBy", ["Contract"], ["Guarantor"], [], None, "由担保人担保", "主合同所对应的担保人。"),
    ("underGuarantee", ["GuaranteeContract"], ["Contract"], ["functional"], None,
     "被担保主合同", "担保合同所担保的主债权合同。"),
    ("secures", ["GuaranteeContract"], ["Collateral"], [], None, "担保物", "担保合同项下对应的押品。"),

    # --- 定价与利率 ---
    ("hasInterestRate", ["FinancialProduct"], ["InterestRate"], [], None, "适用利率", "产品所适用的利率定义。"),
    ("appliesRate", ["Account"], ["ExecutingRate"], ["functional"], None, "账户执行利率", "账户实际执行的利率。"),
    ("basedOnBenchmark", ["ExecutingRate"], ["BenchmarkRate"], ["functional"], None,
     "挂钩基准利率", "执行利率所挂钩的基准利率。"),
    ("hasFeeItem", ["FinancialProduct"], ["FeeItem"], [], None, "适用收费项目", "产品所适用的收费项目。"),
    ("inFeeSchedule", ["FeeItem"], ["FeeSchedule"], ["functional"], None, "所属价目表", "收费项目所归属的价目表。"),

    # --- 反洗钱与尽职调查 ---
    ("hasRiskLevel", ["Customer"], ["CustomerRiskLevel"], ["functional"], None,
     "客户风险等级", "客户在反洗钱口径下的风险评级结果。"),
    ("subjectToDueDiligence", ["Customer"], ["DueDiligence"], [], None, "开展尽职调查", "对客户开展的尽职调查活动。"),
    ("screenedBy", ["BankParty"], ["SanctionsScreening"], [], None, "经制裁筛查", "对参与方开展的制裁名单筛查。"),

    # --- 资本计量与风险缓释 ---
    ("mitigatedBy", ["Exposure"], ["RiskMitigation"], [], None, "由缓释安排覆盖", "降低该敞口风险的风险缓释安排。"),
    ("hasProvision", ["LoanAccount"], ["Provision"], [], None, "计提拨备", "贷款账户所计提的损失准备。"),
    ("impairs", ["Impairment"], ["LoanAccount"], ["functional"], None, "减值对象", "发生减值的贷款账户。"),
    ("basedOnRWA", ["CapitalAdequacy"], ["RiskWeightedAsset"], ["functional"], None,
     "基于风险加权资产", "资本充足率计量所依据的风险加权资产。"),

    # --- 运营与清算 ---
    ("producesError", ["BatchJob"], ["OperationalError"], [], None, "产生差错", "批处理作业执行过程中产生的差错。"),
    ("reconcilesAccount", ["Reconciliation"], ["Account"], [], None, "对账账户", "对账作业所核对的账户。"),
    ("inSession", ["ClearingTransaction"], ["SettlementSession"], ["functional"], None,
     "所属清算场次", "清算交易所归属的清算场次。"),
    ("executedOn", ["BatchJob"], ["TechnicalComponent"], ["functional"], None, "运行于组件", "批处理作业所运行的技术组件。"),
]

# (属性名, 定义域, 值类型, 是否函数性, 中文标签, 注释)
DATA_PROPERTIES = [
    ("partyIdentifier", ["BankParty"], "str", True, "参与方编号", "客户号或员工号，全行唯一。"),
    ("accountNumber", ["Account"], "str", True, "账号", "账户编号，全行唯一。"),
    ("transactionAmount", ["FinancialTransaction"], "float", True, "交易金额", "交易的发生金额。"),
    ("currencyCode", ["FinancialTransaction"], "str", True, "币种代码", "遵循 ISO 4217 的币种代码。"),
    ("transactionTimestamp", ["FinancialTransaction"], "datetime", True, "交易时间", "交易发生的时间戳。"),

    ("fxRate", ["ForeignExchangeTransaction"], "float", True, "成交汇率", "外汇交易执行的兑换汇率。"),
    ("counterCurrencyCode", ["ForeignExchangeTransaction"], "str", True, "对手币种代码", "外汇交易中相对本币的另一币种，遵循 ISO 4217。"),
    ("valueDate", ["ForeignExchangeTransaction"], "datetime", True, "起息日", "外汇交易资金实际交割并计息的日期。"),
    ("remittanceCountryCode", ["CrossBorderTransaction"], "str", True, "汇款国家地区代码", "汇款方所在国家或地区代码，遵循 ISO 3166。"),
    ("beneficiaryCountryCode", ["CrossBorderTransaction"], "str", True, "收款国家地区代码", "收款方所在国家或地区代码，遵循 ISO 3166。"),
    ("declarationNo", ["CrossBorderTransaction"], "str", True, "国际收支申报号", "跨境收付对应的国际收支申报编号。"),
    ("remittanceRefNo", ["CrossBorderTransaction"], "str", True, "汇款参考号", "跨境汇款的报文业务参考号。"),
    ("batchNo", ["AgencyTransaction"], "str", True, "批次号", "代收付交易的批次编号。"),
    ("batchRecordCount", ["AgencyTransaction"], "int", True, "批次笔数", "批次内包含的明细交易笔数。"),
    ("batchTotalAmount", ["AgencyTransaction"], "float", True, "批次总金额", "批次内所有明细交易的金额合计。"),
    ("entrustingPartyName", ["AgencyTransaction"], "str", True, "委托单位名称", "发起代收付委托的单位名称。"),
    ("cardNo", ["CardTransaction"], "str", True, "卡号", "交易使用的银行卡卡号。"),
    ("merchantCode", ["CardTransaction"], "str", True, "商户代码", "受理交易的商户编号。"),
    ("merchantName", ["CardTransaction"], "str", True, "商户名称", "受理交易的商户名称。"),
    ("terminalCode", ["CardTransaction"], "str", True, "受理终端代码", "完成交易受理的终端编号。"),
    ("authorizationCode", ["CardTransaction"], "str", True, "授权码", "发卡行返回的交易授权批准码。"),
    ("discountAmount", ["BillTransaction"], "float", True, "贴现金额", "票据贴现时实际支付给持票人的金额。"),
    ("discountDays", ["BillTransaction"], "int", True, "贴现天数", "自贴现日至票据到期日的实际天数。"),
    ("cashTellerNo", ["CashTransaction"], "str", True, "柜员号", "办理现金收付的柜员编号。"),
    ("cashVoucherNo", ["CashTransaction"], "str", True, "现金凭证号", "现金交易的传票或凭证编号。"),
    ("riskLevel", ["RiskEvent"], "str", True, "风险等级", "风险事件的评级结果。"),
    ("keyLength", ["CryptographicKey"], "int", False, "密钥长度", "密钥的位数长度。"),
    ("algorithmName", ["CryptoAlgorithm"], "str", True, "算法名称", "算法的标准名称，如 SM2、SM4、SM3。"),
    ("reportPeriod", ["RegulatoryReport"], "str", True, "报送期间", "监管报送所覆盖的报告期。"),
    ("reportCode", ["RegulatoryReport"], "str", True, "报文编号", "监管统一规定的报文代码。"),
    ("reportFrequency", ["RegulatoryReport"], "str", True, "报送频度", "报送周期类型，如日报、月报、季报、年报。"),
    ("submissionDeadline", ["RegulatoryReport"], "datetime", True, "报送截止日", "报文提交的最后时限。"),
    ("recordCount", ["RegulatoryReport"], "int", True, "记录条数", "报文包含的数据记录数量。"),
    ("dataItemCode", ["ReportingDataItem"], "str", True, "数据项编号", "监管口径下数据项的编码。"),

    ("eastCustomerCode", ["EASTCustomerItem"], "str", True, "客户编号", "报送口径下唯一标识客户的编号，为源实体属性 BankParty.partyIdentifier 在报送时点的快照值。"),
    ("eastCustomerName", ["EASTCustomerItem"], "str", True, "客户名称", "客户法定全称。"),
    ("eastIdType", ["EASTCustomerItem"], "str", True, "证件类型", "客户身份证件类型代码。"),
    ("eastIdNumber", ["EASTCustomerItem"], "str", True, "证件号码", "客户身份证件号码，反洗钱核查关键字段。"),
    ("eastCustomerType", ["EASTCustomerItem"], "str", True, "客户类型", "个人客户与对公客户的分类代码。"),
    ("eastIndustryCode", ["EASTCustomerItem"], "str", True, "行业代码", "客户所属国民经济行业分类代码。"),
    ("eastRegisteredCapital", ["EASTCustomerItem"], "float", True, "注册资本", "对公客户注册资本金额。"),
    ("eastEstablishDate", ["EASTCustomerItem"], "datetime", True, "成立日期", "对公客户工商登记成立日期。"),
    ("eastRegisterAddress", ["EASTCustomerItem"], "str", True, "注册地址", "客户登记注册地址。"),

    ("eastAccountNo", ["EASTAccountItem"], "str", True, "账号", "报送口径下的账户编号，为源实体属性 Account.accountNumber 在报送时点的快照值。"),
    ("eastAccountType", ["EASTAccountItem"], "str", True, "账户类型", "账户种类代码，如基本户、一般户、专用户。"),
    ("eastAccountCurrency", ["EASTAccountItem"], "str", True, "账户币种", "账户记账币种代码。"),
    ("eastOpenOrgCode", ["EASTAccountItem"], "str", True, "开户机构代码", "开立账户的机构编码。"),
    ("eastOpenDate", ["EASTAccountItem"], "datetime", True, "开户日期", "账户开立日期。"),
    ("eastAccountStatus", ["EASTAccountItem"], "str", True, "账户状态", "账户状态代码，如正常、久悬、销户。"),
    ("eastAccountBalance", ["EASTAccountItem"], "float", True, "账户余额", "报送时点的账户余额。"),

    ("eastDepositType", ["EASTDepositItem"], "str", True, "存款种类", "存款产品种类代码，如活期、定期、大额存单。"),
    ("eastDepositAmount", ["EASTDepositItem"], "float", True, "存款金额", "存款本金金额。"),
    ("eastValueDate", ["EASTDepositItem"], "datetime", True, "起息日", "存款开始计息日期。"),
    ("eastMaturityDate", ["EASTDepositItem"], "datetime", True, "到期日", "存款到期日期。"),
    ("eastInterestRate", ["EASTDepositItem"], "float", True, "存款利率", "存款执行年利率。"),
    ("eastDepositTerm", ["EASTDepositItem"], "str", True, "存期", "存款期限，如三个月、六个月、一年。"),

    ("eastLoanNo", ["EASTLoanItem"], "str", True, "借据编号", "贷款借据的唯一编号。"),
    ("eastContractNo", ["EASTLoanItem"], "str", True, "合同编号", "贷款合同编号。"),
    ("eastLoanProduct", ["EASTLoanItem"], "str", True, "贷款品种", "贷款产品品种代码。"),
    ("eastLoanAmount", ["EASTLoanItem"], "float", True, "贷款金额", "贷款合同金额。"),
    ("eastLoanBalance", ["EASTLoanItem"], "float", True, "贷款余额", "报送时点贷款本金余额。"),
    ("eastIssueDate", ["EASTLoanItem"], "datetime", True, "发放日期", "贷款实际发放日期。"),
    ("eastLoanMaturityDate", ["EASTLoanItem"], "datetime", True, "贷款到期日", "贷款合同约定到期日期。"),
    ("eastLoanRate", ["EASTLoanItem"], "float", True, "贷款利率", "贷款执行年利率。"),
    ("eastGuaranteeType", ["EASTLoanItem"], "str", True, "担保方式", "信用、保证、抵押、质押等担保方式代码。"),
    ("eastFiveClass", ["EASTLoanItem"], "str", True, "五级分类", "正常、关注、次级、可疑、损失分类结果。"),
    ("eastRepayMethod", ["EASTLoanItem"], "str", True, "还款方式", "等额本息、到期一次还本付息等方式代码。"),

    ("eastTxnSerialNo", ["EASTTransactionItem"], "str", True, "交易流水号", "交易的唯一流水编号。"),
    ("eastTxnAmount", ["EASTTransactionItem"], "float", True, "交易金额", "交易发生金额，为源实体属性 FinancialTransaction.transactionAmount 在报送时点的快照值。"),
    ("eastTxnDirection", ["EASTTransactionItem"], "str", True, "交易方向", "资金收付方向，如借、贷。"),
    ("eastTxnType", ["EASTTransactionItem"], "str", True, "交易类型", "交易品种分类代码。"),
    ("eastTxnTime", ["EASTTransactionItem"], "datetime", True, "交易时间", "交易发生时间戳，为源实体属性 FinancialTransaction.transactionTimestamp 在报送时点的快照值。"),
    ("eastCounterAccount", ["EASTTransactionItem"], "str", True, "对手账号", "交易对手方账号。"),
    ("eastCounterName", ["EASTTransactionItem"], "str", True, "对手名称", "交易对手方名称。"),
    ("eastTxnSummary", ["EASTTransactionItem"], "str", True, "交易摘要", "交易用途或摘要说明。"),
    ("eastTxnChannel", ["EASTTransactionItem"], "str", True, "交易渠道", "交易发生的渠道代码。"),
    ("eastPostBalance", ["EASTTransactionItem"], "float", True, "交易后余额", "交易发生后账户余额。"),

    ("eastBillNo", ["EASTBillItem"], "str", True, "票据号码", "票据的唯一票号，票交所口径唯一标识，为源实体属性 Bill.billNo 在报送时点的快照值。"),
    ("eastBillType", ["EASTBillItem"], "str", True, "票据类型", "票据种类代码，如银行承兑汇票、商业承兑汇票。"),
    ("eastDrawerName", ["EASTBillItem"], "str", True, "出票人名称", "票据出票人的法定名称。"),
    ("eastDrawerAccount", ["EASTBillItem"], "str", True, "出票人账号", "出票人在本行的结算账号。"),
    ("eastPayeeName", ["EASTBillItem"], "str", True, "收款人名称", "票据收款人的法定名称。"),
    ("eastAcceptorName", ["EASTBillItem"], "str", True, "承兑人名称", "承担票据到期付款责任的承兑人名称。"),
    ("eastBillAmount", ["EASTBillItem"], "float", True, "票面金额", "票据票面记载的金额，为源实体属性 Bill.billAmount 在报送时点的快照值。"),
    ("eastBillIssueDate", ["EASTBillItem"], "datetime", True, "出票日期", "票据签发日期。"),
    ("eastBillMaturityDate", ["EASTBillItem"], "datetime", True, "票据到期日", "票据约定付款到期日期，为源实体属性 Bill.billMaturityDate 在报送时点的快照值。"),
    ("eastDiscountRate", ["EASTBillItem"], "float", True, "贴现利率", "办理贴现时执行的年利率。"),
    ("eastDiscountAmount", ["EASTBillItem"], "float", True, "贴现金额", "扣除贴现利息后实际支付给申请人的金额。"),
    ("eastBillStatus", ["EASTBillItem"], "str", True, "票据状态", "票据状态代码，如正常、已贴现、已结清、逾期、拒付。"),

    ("eastInterbankNo", ["EASTInterbankItem"], "str", True, "同业业务编号", "同业业务合同或成交单的唯一编号。"),
    ("eastCounterpartyCode", ["EASTInterbankItem"], "str", True, "交易对手机构代码", "同业交易对手的金融机构编码。"),
    ("eastCounterpartyName", ["EASTInterbankItem"], "str", True, "交易对手机构名称", "同业交易对手机构的法定全称。"),
    ("eastCounterpartyType", ["EASTInterbankItem"], "str", True, "交易对手类型", "交易对手机构类型代码，如政策性银行、商业银行、非银金融机构。"),
    ("eastInterbankType", ["EASTInterbankItem"], "str", True, "同业业务类型", "同业业务品种代码，如拆借、存放、买入返售、同业存单。"),
    ("eastInterbankAmount", ["EASTInterbankItem"], "float", True, "同业业务金额", "同业业务成交本金金额，为源实体属性 InterbankBusiness.interbankAmount 在报送时点的快照值。"),
    ("eastInterbankRate", ["EASTInterbankItem"], "float", True, "同业利率", "同业业务执行的年利率，为源实体属性 InterbankBusiness.interbankRate 在报送时点的快照值。"),
    ("eastInterbankStartDate", ["EASTInterbankItem"], "datetime", True, "同业起息日", "同业业务开始计息日期。"),
    ("eastInterbankEndDate", ["EASTInterbankItem"], "datetime", True, "同业到期日", "同业业务约定到期日期。"),
    ("eastInterbankTerm", ["EASTInterbankItem"], "str", True, "业务期限", "同业业务期限，如隔夜、7天、1个月、1年。"),
    ("eastInterbankBalance", ["EASTInterbankItem"], "float", True, "同业业务余额", "报送时点同业业务的本金余额。"),

    ("eastProductCode", ["EASTWealthItem"], "str", True, "产品代码", "理财产品的唯一登记编码。"),
    ("eastProductName", ["EASTWealthItem"], "str", True, "产品名称", "理财产品的对外销售名称。"),
    ("eastProductType", ["EASTWealthItem"], "str", True, "产品类型", "产品形态代码，如净值型、预期收益型、结构性。"),
    ("eastProductRiskRating", ["EASTWealthItem"], "str", True, "产品风险等级", "理财产品风险评级，如 R1 至 R5，为源实体属性 WealthManagementProduct.productRiskRating 在报送时点的快照值。"),
    ("eastProductScale", ["EASTWealthItem"], "float", True, "产品募集规模", "理财产品累计募集金额。"),
    ("eastProductNetValue", ["EASTWealthItem"], "float", True, "产品单位净值", "报送时点理财产品单位净值，为源实体属性 WealthManagementProduct.productNetValue 在该时点的快照值。"),
    ("eastProductIssueDate", ["EASTWealthItem"], "datetime", True, "产品成立日", "理财产品正式成立起算日期。"),
    ("eastProductMaturityDate", ["EASTWealthItem"], "datetime", True, "产品到期日", "理财产品约定到期日期。"),
    ("eastProductTerm", ["EASTWealthItem"], "str", True, "产品期限", "理财产品的存续期限。"),
    ("eastSubscriptionAmount", ["EASTWealthItem"], "float", True, "认购金额", "客户认购理财产品的金额。"),
    ("eastReturnType", ["EASTWealthItem"], "str", True, "收益类型", "收益特征代码，如保本浮动收益、非保本浮动收益。"),
    ("eastRedemptionStatus", ["EASTWealthItem"], "str", True, "赎回状态", "客户持有份额的赎回状态代码，如持有中、已赎回、部分赎回。"),

    ("eastOffBalanceNo", ["EASTOffBalanceItem"], "str", True, "表外业务编号", "表外业务合同或凭证的唯一编号。"),
    ("eastOffBalanceType", ["EASTOffBalanceItem"], "str", True, "表外业务类型", "表外业务品种代码，如保函、信用证、承兑、承诺、衍生品。"),
    ("eastOffBalanceAmount", ["EASTOffBalanceItem"], "float", True, "表外业务金额", "表外业务合同名义金额，为源实体属性 OffBalanceCommitment.commitmentAmount 在报送时点的快照值。"),
    ("eastOffBalanceBalance", ["EASTOffBalanceItem"], "float", True, "表外业务余额", "报送时点表外业务的敞口余额。"),
    ("eastApplicantName", ["EASTOffBalanceItem"], "str", True, "申请人名称", "申请开立表外业务凭证的客户名称。"),
    ("eastBeneficiaryName", ["EASTOffBalanceItem"], "str", True, "受益人名称", "表外业务项下的受益人名称。"),
    ("eastOffBalanceIssueDate", ["EASTOffBalanceItem"], "datetime", True, "开立日期", "表外业务凭证开立日期。"),
    ("eastOffBalanceExpiryDate", ["EASTOffBalanceItem"], "datetime", True, "失效日期", "表外业务凭证到期或失效日期，为源实体属性 OffBalanceCommitment.commitmentExpiryDate 在报送时点的快照值。"),
    ("eastMarginRatio", ["EASTOffBalanceItem"], "float", True, "保证金比例", "表外业务缴存保证金占业务金额的比例。"),
    ("eastMarginAmount", ["EASTOffBalanceItem"], "float", True, "保证金金额", "表外业务缴存的保证金金额。"),
    ("eastConversionFactor", ["EASTOffBalanceItem"], "float", True, "信用转换系数", "表外业务转换为表内风险敞口的监管系数。"),
    ("eastWeightedAmount", ["EASTOffBalanceItem"], "float", True, "加权风险资产额", "表外业务按转换系数折算后的加权风险资产。"),

    ("reportedPeriod", ["EASTDataItem"], "str", True, "报送期间", "报送记录所归属的报告期，用于区分同一实体的多期报送记录。"),
    ("snapshotTime", ["EASTDataItem"], "datetime", True, "快照时点", "报送数据自源系统抽取并冻结的时点，归档后不随源数据变动。"),

    ("billNo", ["Bill"], "str", True, "票据号码", "票据的唯一票号。"),
    ("billAmount", ["Bill"], "float", True, "票面金额", "票据票面记载的金额。"),
    ("billMaturityDate", ["Bill"], "datetime", True, "票据到期日", "票据约定付款到期日期。"),
    ("interbankAmount", ["InterbankBusiness"], "float", True, "同业业务金额", "同业业务成交本金金额。"),
    ("interbankRate", ["InterbankBusiness"], "float", True, "同业利率", "同业业务执行年利率。"),
    ("commitmentAmount", ["OffBalanceCommitment"], "float", True, "承诺金额", "表外承担的合同名义金额。"),
    ("commitmentExpiryDate", ["OffBalanceCommitment"], "datetime", True, "失效日期", "表外承担到期或失效日期。"),
    ("productNetValue", ["WealthManagementProduct"], "float", True, "产品单位净值", "理财产品当前单位净值。"),
    ("productRiskRating", ["WealthManagementProduct"], "str", True, "产品风险等级", "理财产品风险评级，如 R1 至 R5。"),

    ("collateralValue", ["Collateral"], "float", True, "押品评估价值", "押品经评估确认的价值。"),
    ("assessmentDate", ["Collateral"], "datetime", True, "评估基准日", "押品价值的评估基准日期。"),
    ("collateralCurrency", ["Collateral"], "str", True, "押品币种", "押品价值计量所采用的币种代码。"),
    ("beneficialOwnerRatio", ["BeneficialOwner"], "float", True, "受益持股比例", "受益所有人对客户主体的持股比例。"),
    ("ratingValue", ["CreditRating"], "str", True, "评级结果", "信用评级结论，如 AAA、AA、A 等等级。"),
    ("ratingAgency", ["CreditRating"], "str", True, "评级机构", "出具评级结果的机构名称。"),
    ("ratingDate", ["CreditRating"], "datetime", True, "评级日期", "评级结果出具的日期。"),
    ("limitAmount", ["CreditLimit"], "float", True, "额度金额", "核定授信额度的金额。"),
    ("limitExpiryDate", ["CreditLimit"], "datetime", True, "额度到期日", "授信额度失效日期。"),
    ("indicatorValue", ["RiskIndicator"], "float", True, "指标值", "风险指标的当前取值。"),
    ("indicatorThreshold", ["RiskIndicator"], "float", True, "预警阈值", "触发风险预警的指标阈值。"),
    ("userAccountName", ["UserAccount"], "str", True, "账号名称", "系统账号的登录名。"),
    ("userAccountStatus", ["UserAccount"], "str", True, "账号状态", "系统账号状态，如正常、锁定、停用、注销。"),
    ("standardCode", ["DataStandard"], "str", True, "标准编号", "数据标准的统一编号。"),
    ("modelVersion", ["DataModel"], "str", True, "模型版本", "数据模型的版本号。"),

    # --- 映射元数据域数据属性 ---
    ("specVersion", ["MappingSpecification"], "str", True, "规格版本", "映射规格的版本号。"),
    ("specScope", ["MappingSpecification"], "str", True, "报送口径", "映射规格所面向的报送口径，如 EAST5.0、一表通2.1。"),
    ("specEffectiveDate", ["MappingSpecification"], "str", True, "生效日期", "映射规格生效的报告期起始日。"),
    ("mappingCode", ["FieldMapping"], "str", True, "映射编号", "字段映射条目的唯一编号。"),
    ("targetOntologyProperty", ["FieldMapping"], "str", True, "目标本体属性", "映射目标在本体中的数据属性名，如 eastAccountNo。因本体属性是属性而非实例，只能以名称引用。"),
    ("targetDomainClass", ["FieldMapping"], "str", True, "目标本体类", "映射目标属性所属的主题域类，如 EASTAccountItem。"),
    ("targetOfficialCode", ["FieldMapping"], "str", True, "官方数据项编号", "监管规范下发的数据项编号，待标准到位后填写。"),
    ("targetOfficialName", ["FieldMapping"], "str", True, "官方字段名", "监管规范中的正式字段名，待标准到位后校准。"),
    ("sourceSystemName", ["FieldMapping"], "str", True, "源系统名称", "取数来源的业务系统名称。"),
    ("sourceTableCode", ["FieldMapping"], "str", True, "源表代码", "取数来源的表名。"),
    ("sourceFieldCode", ["FieldMapping"], "str", True, "源字段代码", "取数来源的字段名。"),
    ("sourceFieldType", ["FieldMapping"], "str", True, "源字段类型", "源字段的类型与长度，如 VARCHAR(32)、DECIMAL(18,2)。"),
    ("transformationType", ["FieldMapping"], "str", True, "转换类型", "加工方式：直接映射、代码转换、计算派生、常量赋值、字符串拼接、条件分支。"),
    ("transformationExpression", ["FieldMapping"], "str", True, "转换表达式", "加工逻辑的可执行描述，供转换引擎解析。"),
    ("defaultValue", ["FieldMapping"], "str", True, "缺省值", "源值为空时填报的默认值。"),
    ("isRequired", ["FieldMapping"], "bool", True, "是否必填", "该报送字段在监管口径下是否必填。"),
    ("mappingStatus", ["FieldMapping"], "str", True, "映射状态", "取值：未映射、待确认、已确认、不适用。"),
    ("mappingConfidence", ["FieldMapping"], "str", True, "映射置信度", "取值：拟定、已校准、已验证。拟定表示尚未对照官方规范。"),
    ("mappingNote", ["FieldMapping"], "str", True, "映射备注", "映射条目的补充说明与待办事项。"),
    ("tableName", ["SourceTable"], "str", True, "表名", "源系统表的物理表名。"),
    ("systemName", ["SourceTable"], "str", True, "所属系统", "源系统表所属的业务系统。"),
    ("tableComment", ["SourceTable"], "str", True, "表说明", "源系统表的业务含义说明。"),
    ("fieldName", ["SourceField"], "str", True, "字段名", "源表字段的物理字段名。"),
    ("fieldType", ["SourceField"], "str", True, "字段类型", "源字段的类型与长度。"),
    ("fieldNullable", ["SourceField"], "bool", True, "可否为空", "源字段在源系统中是否允许为空。"),
    ("ruleExpression", ["TransformationRule"], "str", True, "规则表达式", "转换规则的可执行描述。"),
    ("sourceCodeValue", ["CodeMapping"], "str", True, "源代码值", "源系统中的代码取值。"),
    ("targetCodeValue", ["CodeMapping"], "str", True, "目标代码值", "监管口径下的代码取值。"),
    ("codeTableName", ["CodeMapping"], "str", True, "代码表名称", "该对照条目所属的代码表。"),
    ("coverageRatio", ["MappingCoverage"], "float", True, "覆盖率", "已确认映射字段数占应映射字段总数的比例。"),
    ("mappedCount", ["MappingCoverage"], "int", True, "已映射数", "已建立映射的字段数量。"),
    ("unmappedCount", ["MappingCoverage"], "int", True, "未映射数", "尚未建立映射的字段数量。"),
    ("checkDate", ["MappingCoverage"], "datetime", True, "校验日期", "覆盖率快照的生成时间。"),

    # --- 机构层级与岗位 ---
    ("organizationCode", ["InternalOrganization"], "str", True, "机构代码", "机构在全行组织树中的唯一编码。"),
    ("organizationLevel", ["InternalOrganization"], "str", True, "机构层级", "机构层级，如总行、分行、支行、网点。"),
    ("positionCode", ["Position"], "str", True, "岗位编码", "岗位在机构内的唯一编码。"),
    ("positionTitle", ["Position"], "str", True, "岗位名称", "岗位的名称。"),

    # --- 会计账务域 ---
    ("subjectCode", ["AccountingSubject"], "str", True, "科目代码", "会计科目的编码。"),
    ("subjectName", ["AccountingSubject"], "str", True, "科目名称", "会计科目的名称。"),
    ("balanceDirection", ["AccountingSubject"], "str", True, "余额方向", "科目正常余额所在方向，借或贷。"),
    ("voucherNo", ["AccountingVoucher"], "str", True, "凭证号", "记账凭证的编号。"),
    ("accountingDate", ["AccountingVoucher"], "datetime", True, "记账日期", "凭证的账务处理日期。"),
    ("entryAmount", ["AccountingEntry"], "float", True, "分录金额", "分录的发生金额。"),
    ("entrySummary", ["AccountingEntry"], "str", True, "分录摘要", "分录的业务摘要说明。"),
    ("periodCode", ["AccountingPeriod"], "str", True, "期间代码", "会计期间的编码。"),
    ("periodStartDate", ["AccountingPeriod"], "datetime", True, "期间起始日", "会计期间的开始日期。"),
    ("periodEndDate", ["AccountingPeriod"], "datetime", True, "期间结束日", "会计期间的结束日期。"),
    ("periodStatus", ["AccountingPeriod"], "str", True, "期间状态", "会计期间状态，如未结账、已结账、已关账。"),
    ("ledgerBalance", ["Ledger"], "float", True, "账簿余额", "账簿在某一时点的余额。"),

    # --- 担保与保证 ---
    ("guarantorIdentifier", ["Guarantor"], "str", True, "担保人编号", "担保人的唯一编号。"),
    ("guaranteeContractNo", ["GuaranteeContract"], "str", True, "担保合同编号", "担保合同的唯一编号。"),
    ("guaranteeAmount", ["GuaranteeContract"], "float", True, "担保金额", "担保合同所担保的金额。"),
    ("guaranteeMethod", ["GuaranteeContract"], "str", True, "担保方式", "担保方式，如保证、抵押、质押。"),

    # --- 定价与利率 ---
    ("rateCode", ["InterestRate"], "str", True, "利率代码", "利率的唯一编码。"),
    ("rateValue", ["InterestRate"], "float", True, "利率值", "利率的取值。"),
    ("rateType", ["InterestRate"], "str", True, "利率类型", "利率的期限口径，如年利率、月利率、日利率。"),
    ("effectiveDate", ["InterestRate"], "datetime", True, "利率生效日", "利率开始适用的日期。"),
    ("benchmarkRateName", ["BenchmarkRate"], "str", True, "基准利率名称", "基准利率的名称，如 LPR、Shibor。"),
    ("floatingMode", ["ExecutingRate"], "str", True, "浮动方式", "利率的确定方式，如固定、浮动。"),
    ("floatingBasisPoint", ["ExecutingRate"], "float", True, "加减基点", "在基准利率基础上加减的基点数值。"),
    ("feeItemCode", ["FeeItem"], "str", True, "收费项目代码", "收费项目的编码。"),
    ("feeRate", ["FeeItem"], "float", True, "费率", "收费项目的费率。"),
    ("feeBasis", ["FeeItem"], "str", True, "计费基准", "计费依据，如按笔、按比例、按金额区间。"),
    ("scheduleVersion", ["FeeSchedule"], "str", True, "价目表版本", "价目表的版本号。"),

    # --- 反洗钱与尽职调查 ---
    ("riskLevelCode", ["CustomerRiskLevel"], "str", True, "风险等级代码", "客户风险等级的编码。"),
    ("riskLevelName", ["CustomerRiskLevel"], "str", True, "风险等级名称", "客户风险等级名称，如低、中、高。"),
    ("riskLevelAssessDate", ["CustomerRiskLevel"], "datetime", True, "评级日期", "客户风险等级的评定日期。"),
    ("dueDiligenceDate", ["DueDiligence"], "datetime", True, "尽调日期", "尽职调查的开展日期。"),
    ("dueDiligenceResult", ["DueDiligence"], "str", True, "尽调结论", "尽职调查的结论。"),
    ("reportNo", ["SuspiciousTransactionReport"], "str", True, "可疑报告编号", "可疑交易报告的编号。"),
    ("reportDate", ["SuspiciousTransactionReport"], "datetime", True, "报告日期", "报告的报送日期。"),
    ("largeReportNo", ["LargeAmountTransactionReport"], "str", True, "大额报告编号", "大额交易报告的编号。"),
    ("largeReportDate", ["LargeAmountTransactionReport"], "datetime", True, "大额报告日期", "大额交易报告的报送日期。"),
    ("screeningResult", ["SanctionsScreening"], "str", True, "筛查结果", "制裁名单筛查的结果，如无命中、疑似命中、确认命中。"),
    ("screeningDate", ["SanctionsScreening"], "datetime", True, "筛查日期", "制裁名单筛查的执行日期。"),
    ("screeningListName", ["SanctionsScreening"], "str", True, "名单名称", "筛查所依据的名单名称。"),

    # --- 资本计量与风险缓释 ---
    ("exposureAmount", ["Exposure"], "float", True, "敞口金额", "风险敞口的暴露金额。"),
    ("riskWeight", ["RiskWeightedAsset"], "float", True, "风险权重", "该类资产适用的风险权重。"),
    ("weightedAssetAmount", ["RiskWeightedAsset"], "float", True, "风险加权资产额", "按风险权重折算后的资产金额。"),
    ("provisionAmount", ["Provision"], "float", True, "拨备金额", "计提的拨备金额。"),
    ("provisionRatio", ["Provision"], "float", True, "拨备率", "拨备占对应资产余额的比例。"),
    ("impairmentAmount", ["Impairment"], "float", True, "减值金额", "确认的减值金额。"),
    ("impairmentStage", ["Impairment"], "str", True, "减值阶段", "预期信用损失模型的阶段划分，一至三阶段。"),
    ("capitalRatio", ["CapitalAdequacy"], "float", True, "资本充足率", "资本与风险加权资产的比率。"),
    ("tierOneRatio", ["CapitalAdequacy"], "float", True, "一级资本充足率", "一级资本净额占风险加权资产的比例。"),
    ("mitigationType", ["RiskMitigation"], "str", True, "缓释类型", "风险缓释手段类型，如押品、保证、净额结算。"),

    # --- 运营与清算 ---
    ("batchJobCode", ["BatchJob"], "str", True, "作业编码", "批处理作业的编码。"),
    ("batchJobStatus", ["BatchJob"], "str", True, "作业状态", "批处理作业状态，如待运行、运行中、成功、失败。"),
    ("batchStartTime", ["BatchJob"], "datetime", True, "作业开始时间", "批处理作业的开始时间。"),
    ("batchEndTime", ["BatchJob"], "datetime", True, "作业结束时间", "批处理作业的结束时间。"),
    ("reconStatus", ["Reconciliation"], "str", True, "对账状态", "对账作业的状态，如相符、有差异、已处理。"),
    ("reconDifference", ["Reconciliation"], "float", True, "差异金额", "对账发现的差异金额。"),
    ("errorCode", ["OperationalError"], "str", True, "差错编号", "运营差错的编号。"),
    ("errorStatus", ["OperationalError"], "str", True, "差错状态", "差错处理状态，如待更正、已更正、已关闭。"),
    ("sessionNo", ["SettlementSession"], "str", True, "场次编号", "清算场次的编号。"),
    ("sessionTime", ["SettlementSession"], "datetime", True, "场次时间", "清算场次的开始时间。"),
]

# 不相交类组
DISJOINT_GROUPS = [
    ["PersonalCustomer", "CorporateCustomer"],
    ["DepositAccount", "LoanAccount", "SettlementAccount"],
    ["SystemAdministrationRole", "BusinessOperationRole", "AuditRole", "SupervisionRole"],
    ["SymmetricAlgorithm", "AsymmetricAlgorithm", "HashAlgorithm"],
    ["DepositTransaction", "WithdrawalTransaction", "TransferTransaction",
     "PaymentTransaction", "ClearingTransaction", "CashTransaction",
     "CardTransaction", "ForeignExchangeTransaction", "BillTransaction",
     "InvestmentTransaction", "FeeTransaction", "CrossBorderTransaction",
     "AgencyTransaction"],
    ["CardPurchaseTransaction", "CardCashWithdrawalTransaction",
     "CardRefundTransaction"],
    ["FXSpotTransaction", "FXForwardTransaction", "FXSwapTransaction"],
    ["BillAcceptanceTransaction", "BillDiscountTransaction",
     "BillRediscountTransaction", "BillSettlementTransaction"],
    ["WealthSubscriptionTransaction", "WealthRedemptionTransaction"],
    ["FeeChargeTransaction", "InterestSettlementTransaction"],
    ["InwardRemittanceTransaction", "OutwardRemittanceTransaction"],
    ["AgencyCollectionTransaction", "AgencyPaymentTransaction",
     "BatchDebitTransaction", "BatchCreditTransaction"],
    ["RegulatoryBody", "CorrespondentBank"],
    ["EASTReport", "StatutoryReport1104", "AMLReport", "CreditRegistryReport",
     "FinancialStatisticsReport", "PaymentSettlementReport"],
    ["CreditRiskEvent", "MarketRiskEvent", "OperationalRiskEvent",
     "LiquidityRiskEvent", "ComplianceRiskEvent"],
    ["EASTCustomerItem", "EASTAccountItem", "EASTDepositItem",
     "EASTLoanItem", "EASTTransactionItem", "EASTBillItem",
     "EASTInterbankItem", "EASTWealthItem", "EASTOffBalanceItem"],
    ["BankAcceptanceBill", "CommercialAcceptanceBill"],
    ["InterbankLending", "InterbankDeposit", "ReverseRepo", "InterbankCD"],
    ["Guarantee", "LetterOfCredit", "AcceptanceCommitment",
     "CreditCommitment", "DerivativeContract"],
    ["DemandDepositProduct", "TimeDepositProduct", "LargeCDProduct"],
    ["WorkingCapitalLoanProduct", "ProjectLoanProduct",
     "ConsumerLoanProduct", "MortgageLoanProduct"],
    ["AgencyBusiness", "GuaranteeBusiness",
     "CommitmentBusiness", "TradingAgencyBusiness"],
    ["CashCollateral", "RealEstateCollateral", "ReceivablesCollateral",
     "SecuritiesCollateral", "MovableCollateral"],
    ["MappingSpecification", "FieldMapping", "SourceTable", "SourceField",
     "TransformationRule", "CodeMapping", "MappingCoverage"],
    ["HeadOffice", "Branch", "Department"],
    ["AssetSubject", "LiabilitySubject", "EquitySubject",
     "IncomeSubject", "ExpenseSubject"],
    ["GeneralLedger", "SubLedger"],
    ["CorporateGuarantor", "PersonalGuarantor"],
    ["SuretyshipContract", "MortgageContract", "PledgeContract"],
    ["BenchmarkRate", "ExecutingRate"],
    ["SimplifiedDueDiligence", "StandardDueDiligence", "EnhancedDueDiligence"],
    ["CreditExposure", "MarketExposure", "OperationalExposure"],
]

# (类名, 属性名, 限制类型, 目标类, 基数)  限制类型: some | only | min | max | exactly | value
RESTRICTIONS = [
    ("DepositAccount", "appliesProduct", "some", "DepositProduct", None),
    ("LoanAccount", "appliesProduct", "some", "LoanProduct", None),
    ("TransferTransaction", "involvesAccount", "min", "Account", 2),
    ("BillTransaction", "involvesBill", "some", "Bill", None),
    ("InvestmentTransaction", "involvesInvestmentProduct", "some", "WealthManagementProduct", None),
    ("AgencyTransaction", "underAgreement", "some", "AgencyAgreement", None),
    ("FinancialTransaction", "viaChannel", "some", "ServiceChannel", None),
    ("AuditRecord", "signedWith", "some", "AsymmetricAlgorithm", None),
    ("RegulatoryReport", "submittedTo", "some", "RegulatoryBody", None),
    ("RegulatoryReport", "submittedBy", "some", "InternalOrganization", None),
    ("RegulatoryReport", "inBatch", "some", "ReportingBatch", None),
    ("RegulatoryReport", "producedFrom", "some", "DataSet", None),
    ("AMLReport", "hasDataItem", "min", "ReportingDataItem", 1),
    ("EASTReport", "hasDataItem", "some", "EASTDataItem", None),
    ("ReportingDataItem", "governedByRule", "some", "ReportingRule", None),

    ("EASTCustomerItem", "reportsEntity", "some", "Customer", None),
    ("EASTAccountItem", "reportsEntity", "some", "Account", None),
    ("EASTDepositItem", "reportsEntity", "some", "DepositAccount", None),
    ("EASTLoanItem", "reportsEntity", "some", "LoanAccount", None),
    ("EASTTransactionItem", "reportsEntity", "some", "FinancialTransaction", None),
    ("EASTBillItem", "reportsEntity", "some", "Bill", None),
    ("EASTInterbankItem", "reportsEntity", "some", "InterbankBusiness", None),
    ("EASTWealthItem", "reportsEntity", "some", "WealthManagementProduct", None),
    ("EASTOffBalanceItem", "reportsEntity", "some", "OffBalanceCommitment", None),

    # 映射元数据域：源字段必须归属某张表，映射条目必须归属某个规格。
    # 刻意不加 FieldMapping ⊑ ∃mapsSourceField.SourceField —— 状态为「未映射」的
    # 条目本就没有源字段，加限制会使其不可满足，反而掩盖覆盖率缺口。
    ("SourceField", "belongsToTable", "some", "SourceTable", None),
    ("FieldMapping", "inSpecification", "some", "MappingSpecification", None),

    # 会计账务域：复式记账要求每笔分录至少各有一借一贷，凭证必须归属会计期间。
    ("AccountingEntry", "debitSubject", "some", "AccountingSubject", None),
    ("AccountingEntry", "creditSubject", "some", "AccountingSubject", None),
    ("AccountingEntry", "inVoucher", "some", "AccountingVoucher", None),
    ("AccountingVoucher", "inPeriod", "some", "AccountingPeriod", None),
    ("GeneralLedger", "subjectOfLedger", "some", "AccountingSubject", None),
    ("SubLedger", "ledgerOfAccount", "some", "Account", None),

    # 担保域：抵押与质押必须有担保物，保证合同无押品故不加此限制，
    # 与 securedBy 不加限制公理（信用贷款无押品）是同一处理原则。
    ("MortgageContract", "secures", "some", "Collateral", None),
    ("PledgeContract", "secures", "some", "Collateral", None),
    ("GuaranteeContract", "underGuarantee", "some", "Contract", None),

    # 反洗钱与资本计量：报告须可追溯到具体交易，减值须有对象。
    ("SuspiciousTransactionReport", "reportsEntity", "some", "FinancialTransaction", None),
    ("LargeAmountTransactionReport", "reportsEntity", "some", "FinancialTransaction", None),
    ("Impairment", "impairs", "some", "LoanAccount", None),
    ("CapitalAdequacy", "basedOnRWA", "some", "RiskWeightedAsset", None),
    ("BatchJob", "executedOn", "some", "TechnicalComponent", None),
]

# SWRL 规则：(规则名, 规则体)
# 说明：SWRL 是单调的，只能「推导/标记」违规，无法「阻止」授权被赋予。
# 真正的强制须在 RBAC 授权服务层实现；这里的作用是离线审计与持续检测。
SWRL_RULES = [
    ("四权分离违规检出",
     "Employee(?e), assignedRole(?e, ?r1), assignedRole(?e, ?r2), "
     "separatedFrom(?r1, ?r2) -> SeparationOfDutyViolation(?e)"),
    ("报送编制复核分离违规检出",
     "Employee(?e), compilesReport(?e, ?r), reviewsReport(?e, ?r) "
     "-> SeparationOfDutyViolation(?e)"),
]

# (类名, 个体名, 中文标签, 注释, 对象属性关系, 数据属性值)
INDIVIDUALS = [
    ("SystemAdministrationRole", "RoleSystemAdmin", "系统管理员", "持有系统管理权的角色实例。",
     {"separatedFrom": ["RoleBusinessOperator", "RoleAuditor", "RoleSupervisor"]}, {}),
    ("BusinessOperationRole", "RoleBusinessOperator", "业务操作员", "持有业务操作权的角色实例。", {}, {}),
    ("AuditRole", "RoleAuditor", "审计员", "持有审计权的角色实例。", {}, {}),
    ("SupervisionRole", "RoleSupervisor", "监督员", "持有监督权的角色实例。", {}, {}),

    ("AsymmetricAlgorithm", "SM2", "SM2 椭圆曲线公钥算法", "国密非对称算法，用于数字签名与密钥交换。", {}, {"algorithmName": "SM2"}),
    ("HashAlgorithm", "SM3", "SM3 密码杂凑算法", "国密摘要算法，用于完整性校验。", {}, {"algorithmName": "SM3"}),
    ("SymmetricAlgorithm", "SM4", "SM4 分组密码算法", "国密对称算法，用于数据加密。", {}, {"algorithmName": "SM4"}),
    ("AsymmetricAlgorithm", "RSA", "RSA 公钥算法", "国际通用非对称算法，用于兼容场景。", {}, {"algorithmName": "RSA"}),
    ("SymmetricAlgorithm", "AES", "AES 分组密码算法", "国际通用对称算法，用于兼容场景。", {}, {"algorithmName": "AES"}),

    ("CounterChannel", "ChannelCounter", "柜面", "网点柜面服务渠道实例。", {}, {}),
    ("InternetBankingChannel", "ChannelInternet", "网上银行", "网上银行渠道实例。", {}, {}),
    ("MobileBankingChannel", "ChannelMobile", "手机银行", "手机银行渠道实例。", {}, {}),
    ("OpenApiChannel", "ChannelOpenApi", "开放银行接口", "开放银行 API 渠道实例。", {}, {}),

    ("CryptoService", "ComponentCrypto", "加密与密钥管理平台", "INFR-01 CRYPTO 平台实例。", {}, {}),
    ("FileTransferService", "ComponentFileTransfer", "统一文件传输平台", "INFR-02 FS 平台实例。", {}, {}),
    ("MessageQueue", "ComponentMessageQueue", "消息中间件平台", "INFR-03 MQ 平台实例。", {}, {}),

    ("RegulatoryBody", "PBOC", "中国人民银行", "负责货币政策、金融统计与征信管理的监管机构。", {}, {}),
    ("RegulatoryBody", "NFRA", "国家金融监督管理总局", "负责银行业保险业监督管理的机构。", {}, {}),
    ("RegulatoryBody", "SAFE", "国家外汇管理局", "负责外汇收支与结售汇监管的机构。", {}, {}),
    ("RegulatoryBody", "CAMLMAC", "中国反洗钱监测分析中心", "接收大额与可疑交易报告的机构。", {}, {}),

    ("ReportingStatus", "StatusDraft", "待编制", "报文尚未开始编制。", {}, {}),
    ("ReportingStatus", "StatusCompiled", "已编制", "报文数据已生成，待复核。", {}, {}),
    ("ReportingStatus", "StatusSubmitted", "已提交", "报文已报送至监管机构。", {}, {}),
    ("ReportingStatus", "StatusAccepted", "已受理", "监管机构已接收并认可报文。", {}, {}),
    ("ReportingStatus", "StatusRejected", "已退回", "报文未通过校验被退回。", {}, {}),
    ("ReportingStatus", "StatusCorrected", "已订正", "退回后完成订正并重新提交。", {}, {}),

    ("ReportingRule", "RuleCustomerIdRequired", "客户证件必填校验", "客户主题域的证件类型与证件号码不得为空。", {}, {}),
    ("ReportingRule", "RuleAmountNonNegative", "金额非负校验", "所有金额类字段取值不得为负数。", {}, {}),
    ("ReportingRule", "RuleCurrencyStandard", "币种规范校验", "币种字段须符合监管口径或 ISO 4217 代码表。", {}, {}),
    ("ReportingRule", "RuleFiveClassDomain", "五级分类取值域校验", "五级分类字段取值须落在五级分类代码表内。", {}, {}),
    ("ReportingRule", "RuleBalanceConsistency", "余额勾稽校验", "交易后余额须等于上笔余额加减本笔交易金额。", {}, {}),
    ("ReportingRule", "RuleAccountCustomerRef", "客户引用完整性校验", "账户主题域的客户编号须在客户主题域中存在。", {}, {}),

    ("ReportingRule", "RuleBillDateOrder", "票据日期序校验", "票据到期日期不得早于出票日期。", {}, {}),
    ("ReportingRule", "RuleBillAmountLimit", "票据金额上限校验", "票面金额不得超过承兑时核定的授信额度。", {}, {}),
    ("ReportingRule", "RuleCounterpartyCode", "同业对手机构编码校验", "同业交易对手机构代码须为有效的金融机构编码。", {}, {}),
    ("ReportingRule", "RuleNetValuePositive", "理财净值正数校验", "理财产品单位净值须为正数。", {}, {}),
    ("ReportingRule", "RuleMarginRatioRange", "保证金比例区间校验", "保证金比例取值须落在 0 与 1 之间。", {}, {}),
    ("ReportingRule", "RuleConversionFactorDomain", "信用转换系数取值域校验", "表外业务信用转换系数须落在监管规定系数表内。", {}, {}),

    # ============ 业务实例层：一个连贯的银行业务切面 ============
    # 设计原则：实例之间用关系串成可追溯链条
    #   机构 → 客户 → 持有产品 → 开立账户 → 发生交易 → 生成审计留痕 → 报送监管
    # 所有员工实例各自只持有一个角色，保证四权分离在主本体中不被 SWRL 判定违规。

    # --- 机构 ---
    ("HeadOffice", "OrgHeadOffice", "总行", "银行法人机构总部。", {}, {"partyIdentifier": "ORG0001"}),
    ("Branch", "OrgBranchShanghai", "上海分行", "负责华东区域业务经营的分支机构。", {}, {"partyIdentifier": "ORG3101"}),

    # --- 客户 ---
    ("CorporateCustomer", "CustHuaxing", "华兴机械制造有限公司", "对公客户，通用设备制造业，内部评级 AA-。",
     {"hasBeneficialOwner": ["BOZhu"], "hasCreditRating": ["RatingHuaxing"],
      "hasCreditLimit": ["LimitHuaxing"],
      "holdsProduct": ["ProdDemandDeposit", "ProdTimeDeposit1Y", "ProdWorkingCapital"],
      "initiatesTransaction": ["TxnDeposit001", "TxnTransfer001", "TxnPay001", "TxnFX001", "TxnRemitOut001"],
      "hasRiskLevel": ["RiskLevelMedium"], "subjectToDueDiligence": ["DDHuaxing"],
      "screenedBy": ["ScreeningHuaxing"]},
     {"partyIdentifier": "C0001"}),
    ("PersonalCustomer", "CustZhang", "张某", "对私客户，持有按揭贷款与理财产品。",
     {"holdsProduct": ["ProdMortgage", "ProdWealthStable"]}, {"partyIdentifier": "C0002"}),
    ("BeneficialOwner", "BOZhu", "朱某", "华兴机械的受益所有人，反洗钱 KYC 核查对象。",
     {}, {"partyIdentifier": "BO0001"}),

    # --- 产品 ---
    ("DemandDepositProduct", "ProdDemandDeposit", "单位活期存款", "可随时存取、按季结息的对公存款产品。", {}, {}),
    ("TimeDepositProduct", "ProdTimeDeposit1Y", "一年期定期存款", "存期一年、到期一次性还本付息的存款产品。", {}, {}),
    ("WorkingCapitalLoanProduct", "ProdWorkingCapital", "流动资金贷款", "满足企业日常经营周转需求的贷款产品。", {}, {}),
    ("MortgageLoanProduct", "ProdMortgage", "个人住房按揭贷款", "以所购住房为抵押的个人中长期贷款产品。", {}, {}),
    ("WealthManagementProduct", "ProdWealthStable", "稳健增利 90 天", "中低风险定开净值型理财产品。",
     {}, {"productNetValue": 1.0325, "productRiskRating": "R2"}),

    # --- 账户 ---
    ("SettlementAccount", "AccHuaxingSettle", "华兴机械结算账户", "华兴机械日常收付结算账户。",
     {}, {"accountNumber": "6228000000000001"}),
    ("DepositAccount", "AccHuaxingTime", "华兴机械定期账户", "华兴机械一年期定期存款账户。",
     {}, {"accountNumber": "6228000000000002"}),
    ("LoanAccount", "AccHuaxingLoan", "华兴机械流贷账户", "流动资金贷款放款与还款账户，以厂房抵押。",
     {"securedBy": ["CollHuaxingPlant"], "appliesRate": ["RateHuaxingLoan"],
      "hasProvision": ["ProvisionHuaxing"], "guaranteedBy": ["GuarantorHengxin"]},
     {"accountNumber": "LD20260001"}),
    ("SettlementAccount", "AccZhangSettle", "张某结算账户", "张某代发工资与日常收付账户。",
     {}, {"accountNumber": "6228000000000003"}),
    ("LoanAccount", "AccZhangMortgage", "张某按揭贷款账户", "张某住房按揭贷款还款账户。",
     {}, {"accountNumber": "LD20260002"}),

    # --- 票据、代理行、委托协议 ---
    ("Bill", "BillHuaxing001", "银行承兑汇票 20260001", "华兴机械签发、本行承兑的银行承兑汇票。",
     {}, {"billNo": "BB20260001", "billAmount": 1000000.00, "billMaturityDate": "2026-12-31"}),
    ("CorrespondentBank", "CorrBankHK", "某境外代理行（中国香港）", "为跨境汇出提供清算通道的境外同业机构。",
     {}, {"partyIdentifier": "CB0001"}),
    ("AgencyAgreement", "AgreementWater", "委托代收水电费协议", "与某市自来水公司签订的批量代扣委托协议。", {}, {}),

    # --- 交易 ---
    ("DepositTransaction", "TxnDeposit001", "华兴机械现金存入", "柜面存入经营回笼资金。",
     {"involvesAccount": ["AccHuaxingSettle"], "viaChannel": ["ChannelCounter"],
      "generatesAuditRecord": ["AuditTransfer001"]},
     {"transactionAmount": 500000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-01T10:12:33"}),
    ("TransferTransaction", "TxnTransfer001", "华兴机械转账至张某", "跨客户转账，同时涉及付款与收款两个账户。",
     {"involvesAccount": ["AccHuaxingSettle", "AccZhangSettle"], "viaChannel": ["ChannelInternet"],
      "generatesAuditRecord": ["AuditTransfer001"], "protectedBy": ["SM2"]},
     {"transactionAmount": 120000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-05T14:26:07"}),
    ("PaymentTransaction", "TxnPay001", "华兴机械支付货款", "向供应商支付采购款项。",
     {"involvesAccount": ["AccHuaxingSettle"], "viaChannel": ["ChannelInternet"]},
     {"transactionAmount": 86000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-08T09:41:18"}),
    ("CardPurchaseTransaction", "TxnCard001", "张某刷卡消费", "张某通过手机银行绑定的银行卡完成消费支付。",
     {"involvesAccount": ["AccZhangSettle"], "viaChannel": ["ChannelMobile"]},
     {"transactionAmount": 1280.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-12T19:03:55",
      "cardNo": "6228000000000003", "merchantCode": "M0001234", "merchantName": "某连锁超市",
      "terminalCode": "T000088", "authorizationCode": "A20260912003"}),
    ("FXSpotTransaction", "TxnFX001", "华兴机械即期结汇", "出口收汇后按即期汇率结汇为人民币。",
     {"involvesAccount": ["AccHuaxingSettle"], "viaChannel": ["ChannelCounter"]},
     {"transactionAmount": 100000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-15T11:20:00",
      "fxRate": 7.1234, "counterCurrencyCode": "USD", "valueDate": "2026-09-17"}),
    ("BatchDebitTransaction", "TxnBatchDebit001", "2026Q3 水电费批量代扣", "依据委托协议批量从签约账户扣收水电费。",
     {"underAgreement": ["AgreementWater"], "viaChannel": ["ChannelOpenApi"]},
     {"transactionAmount": 356000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-20T02:00:00",
      "batchNo": "B20260901", "batchRecordCount": 1200, "batchTotalAmount": 356000.00,
      "entrustingPartyName": "某市自来水公司"}),
    ("BillDiscountTransaction", "TxnDiscount001", "票据贴现", "华兴机械持未到期银承办理贴现。",
     {"involvesBill": ["BillHuaxing001"], "involvesAccount": ["AccHuaxingSettle"],
      "viaChannel": ["ChannelCounter"]},
     {"transactionAmount": 980000.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-22T15:47:12",
      "discountAmount": 980000.00, "discountDays": 87}),
    ("InterestSettlementTransaction", "TxnInterest001", "定期存款结息", "一年期定期存款到期结息。",
     {"involvesAccount": ["AccHuaxingTime"]},
     {"transactionAmount": 3750.00, "currencyCode": "CNY", "transactionTimestamp": "2026-09-21T00:00:00"}),
    ("OutwardRemittanceTransaction", "TxnRemitOut001", "华兴机械跨境汇出", "向境外供应商汇出货款，触发制裁名单筛查预警。",
     {"involvesAccount": ["AccHuaxingSettle"], "viaChannel": ["ChannelCounter"],
      "viaCorrespondentBank": ["CorrBankHK"], "hasRiskEvent": ["RiskEventSanctionHit"]},
     {"transactionAmount": 200000.00, "currencyCode": "USD", "transactionTimestamp": "2026-09-25T16:38:41",
      "remittanceCountryCode": "CN", "beneficiaryCountryCode": "HK",
      "declarationNo": "IBS2026090001", "remittanceRefNo": "RM20260925001"}),

    # --- 风险与授信 ---
    ("CreditRating", "RatingHuaxing", "华兴机械信用评级", "内部评级模型输出的债务人评级结果。",
     {}, {"ratingValue": "AA-", "ratingAgency": "本行内部评级", "ratingDate": "2026-06-30"}),
    ("CreditLimit", "LimitHuaxing", "华兴机械授信额度", "核定的综合授信额度。",
     {}, {"limitAmount": 50000000.00, "limitExpiryDate": "2027-06-30"}),
    ("RealEstateCollateral", "CollHuaxingPlant", "华兴机械厂房抵押", "位于上海某工业区的厂房抵押物。",
     {}, {"collateralValue": 68000000.00, "assessmentDate": "2026-05-20", "collateralCurrency": "CNY"}),
    ("ComplianceRiskEvent", "RiskEventSanctionHit", "制裁名单筛查命中", "跨境汇款收款方命中制裁名单筛查规则。",
     {"measuredBy": ["IndSanctionHits"]}, {}),
    ("RiskIndicator", "IndSanctionHits", "制裁筛查命中次数", "统计周期内制裁筛查命中笔数。",
     {}, {"indicatorValue": 1.0, "indicatorThreshold": 0.0}),

    # --- 审计留痕 ---
    ("AuditRecord", "AuditTransfer001", "转账交易审计记录", "转账交易的不可抵赖留痕，使用 SM2 签名。", {}, {}),

    # --- 员工与系统账号（四权分离：每人仅持一个角色）---
    ("Employee", "EmpZhangSan", "张三（系统管理员）", "持有系统管理权，负责参数配置与账号管理。",
     {"assignedRole": ["RoleSystemAdmin"], "hasUserAccount": ["UaZhangSan"],
      "holdsPosition": ["PosSystemAdmin"]}, {"partyIdentifier": "E0001"}),
    ("Employee", "EmpLiSi", "李四（业务操作员）", "持有业务操作权，负责日常业务办理与报文编制。",
     {"assignedRole": ["RoleBusinessOperator"], "hasUserAccount": ["UaLiSi"],
      "compilesReport": ["ReportEAST2026Q3"], "holdsPosition": ["PosTeller"]}, {"partyIdentifier": "E0002"}),
    ("Employee", "EmpWangWu", "王五（审计员）", "持有审计权，负责日志审计与报文复核。",
     {"assignedRole": ["RoleAuditor"], "hasUserAccount": ["UaWangWu"],
      "reviewsReport": ["ReportEAST2026Q3"], "holdsPosition": ["PosAuditor"]}, {"partyIdentifier": "E0003"}),
    ("Employee", "EmpZhaoLiu", "赵六（监督员）", "持有监督权，负责业务监督与违规处置。",
     {"assignedRole": ["RoleSupervisor"], "hasUserAccount": ["UaZhaoLiu"],
      "holdsPosition": ["PosSupervisor"]}, {"partyIdentifier": "E0004"}),
    ("UserAccount", "UaZhangSan", "zhangsan", "张三的系统账号，状态启用。",
     {}, {"userAccountName": "zhangsan", "userAccountStatus": "启用"}),
    ("UserAccount", "UaLiSi", "lisi", "李四的系统账号，状态启用。",
     {}, {"userAccountName": "lisi", "userAccountStatus": "启用"}),
    ("UserAccount", "UaWangWu", "wangwu", "王五的系统账号，状态启用。",
     {}, {"userAccountName": "wangwu", "userAccountStatus": "启用"}),
    ("UserAccount", "UaZhaoLiu", "zhaoliu", "赵六的系统账号，状态启用。",
     {}, {"userAccountName": "zhaoliu", "userAccountStatus": "启用"}),

    # --- 监管报送 ---
    ("ReportingBatch", "BatchEAST2026Q3", "EAST 2026Q3 报送批次", "2026 年三季度 EAST 报送批次。",
     {"containsReport": ["ReportEAST2026Q3"]}, {}),
    ("EASTReport", "ReportEAST2026Q3", "EAST 2026 年三季度报送报文", "三季度 EAST 报送报文，已提交并受理。",
     {"submittedTo": ["PBOC"], "hasStatus": ["StatusSubmitted"], "inBatch": ["BatchEAST2026Q3"]},
     {"reportCode": "EAST", "reportPeriod": "2026Q3", "reportFrequency": "季报",
      "submissionDeadline": "2026-10-15", "recordCount": 1200}),
    ("EASTCustomerItem", "EASTCustRec001", "客户主题域报送记录（华兴机械）", "华兴机械在 2026Q3 的客户主题域报送快照。",
     {"reportsEntity": ["CustHuaxing"]},
     {"reportedPeriod": "2026Q3", "snapshotTime": "2026-09-30T23:59:59",
      "eastCustomerCode": "C0001", "eastCustomerName": "华兴机械制造有限公司",
      "eastIdType": "统一社会信用代码", "eastIdNumber": "91310000MA1FL0XXXX",
      "eastCustomerType": "对公", "eastIndustryCode": "C34",
      "eastRegisteredCapital": 30000000.00, "eastEstablishDate": "2008-04-16",
      "eastRegisterAddress": "上海市某工业区某路 88 号"}),
    ("EASTAccountItem", "EASTAcctRec001", "账户主题域报送记录（华兴结算户）", "华兴机械结算账户在 2026Q3 的报送快照。",
     {"reportsEntity": ["AccHuaxingSettle"]},
     {"reportedPeriod": "2026Q3", "snapshotTime": "2026-09-30T23:59:59",
      "eastAccountNo": "6228000000000001", "eastAccountType": "单位结算账户",
      "eastAccountCurrency": "CNY", "eastOpenOrgCode": "ORG3101",
      "eastOpenDate": "2020-03-12", "eastAccountStatus": "正常",
      "eastAccountBalance": 1523000.00}),

    # --- 技术组件实例 ---
    ("DatabaseService", "CompDatabase", "核心数据库服务", "承载核心账务数据的关系数据库服务。", {}, {}),
    ("APIGateway", "CompApiGateway", "API 网关", "开放银行接口的统一接入与流量治理组件。", {}, {}),

    # --- 映射元数据实例 ---
    # 边界声明：以下源表名与字段名均为按通用核心系统口径拟定的示例，
    # 未经官方规范与行内数据字典校准，mappingConfidence 一律标注为「拟定」。
    ("MappingSpecification", "SpecEAST2026Q3", "EAST 报送映射规格 2026Q3",
     "2026 年第三季度 EAST 报送的字段映射规格。",
     {"hasFieldMapping": ["MapCustomerCode", "MapCustomerName", "MapIdType",
                          "MapCustomerType", "MapRegisterAddress", "MapIndustryCode",
                          "MapAccountNo", "MapAccountStatus", "MapAccountBalance",
                          "MapOpenDate", "MapAccountCurrency", "MapTxnAmount",
                          "MapTxnDirection"]},
     {"specVersion": "2026Q3-draft", "specScope": "EAST5.0",
      "specEffectiveDate": "2026-07-01"}),

    ("TransformationRule", "RuleDirect", "直接映射", "源字段值原样填报，不做加工。",
     {}, {"ruleExpression": "target = source"}),
    ("TransformationRule", "RuleCodeConversion", "代码转换", "源系统代码按代码表转换为监管口径代码或文本。",
     {}, {"ruleExpression": "target = codeMap[source]"}),
    ("TransformationRule", "RuleComputed", "计算派生", "由一个或多个源字段经计算得到报送值。",
     {}, {"ruleExpression": "target = f(source...)"}),
    ("TransformationRule", "RuleConstant", "常量赋值", "按监管口径填报固定常量值。",
     {}, {"ruleExpression": "target = const"}),
    ("TransformationRule", "RuleConcat", "字符串拼接", "多个源字段按分隔符拼接为报送值。",
     {}, {"ruleExpression": "target = concat(source..., sep)"}),
    ("TransformationRule", "RuleConditional", "条件分支", "依据条件表达式选择不同的取值逻辑。",
     {}, {"ruleExpression": "target = cond ? a : b"}),

    ("CodeMapping", "CodeMapIdType", "证件类型代码对照（10→居民身份证）",
     "核心系统证件类型代码转换为监管口径文本。",
     {}, {"sourceCodeValue": "10", "targetCodeValue": "居民身份证",
          "codeTableName": "证件类型代码表"}),
    ("CodeMapping", "CodeMapAcctStatus", "账户状态代码对照（1→正常）",
     "核心系统账户状态代码转换为监管口径文本。",
     {}, {"sourceCodeValue": "1", "targetCodeValue": "正常",
          "codeTableName": "账户状态代码表"}),
    ("CodeMapping", "CodeMapDrCr", "借贷标志代码对照（D→借）",
     "核心系统借贷标志转换为监管口径交易方向。",
     {}, {"sourceCodeValue": "D", "targetCodeValue": "借",
          "codeTableName": "借贷标志代码表"}),

    ("SourceTable", "TblCoreCustomer", "核心客户信息表", "核心系统承载客户主体信息的表。",
     {"hasSourceField": ["SF_CustNo", "SF_CustName", "SF_IdType", "SF_CustType",
                         "SF_Province", "SF_City", "SF_Address"]},
     {"tableName": "CB_CUSTOMER", "systemName": "核心业务系统",
      "tableComment": "对公与对私客户主体信息主表。"}),
    ("SourceTable", "TblCoreAccount", "核心账户表", "核心系统承载账户信息的表。",
     {"hasSourceField": ["SF_AcctNo", "SF_AcctStatus", "SF_AcctBalance", "SF_AcctOpenDate"]},
     {"tableName": "CB_ACCOUNT", "systemName": "核心业务系统",
      "tableComment": "存款与贷款账户主表。"}),
    ("SourceTable", "TblCoreTransaction", "核心交易流水表", "核心系统承载账务交易流水的表。",
     {"hasSourceField": ["SF_TxnAmt", "SF_DrCrFlag"]},
     {"tableName": "CB_TXN_JOURNAL", "systemName": "核心业务系统",
      "tableComment": "账户级交易流水明细表。"}),

    ("SourceField", "SF_CustNo", "客户号", "核心客户表的客户编号字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "CUST_NO", "fieldType": "VARCHAR(20)", "fieldNullable": False}),
    ("SourceField", "SF_CustName", "客户名称", "核心客户表的客户名称字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "CUST_NAME", "fieldType": "VARCHAR(200)", "fieldNullable": False}),
    ("SourceField", "SF_IdType", "证件类型", "核心客户表的证件类型代码字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "ID_TYPE", "fieldType": "CHAR(2)", "fieldNullable": False}),
    ("SourceField", "SF_CustType", "客户性质", "核心客户表的对公对私标识字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "CUST_KIND", "fieldType": "CHAR(1)", "fieldNullable": False}),
    ("SourceField", "SF_Province", "省份", "核心客户表的注册地址省份字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "REG_PROV", "fieldType": "VARCHAR(40)", "fieldNullable": True}),
    ("SourceField", "SF_City", "城市", "核心客户表的注册地址城市字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "REG_CITY", "fieldType": "VARCHAR(40)", "fieldNullable": True}),
    ("SourceField", "SF_Address", "详细地址", "核心客户表的注册地址明细字段。",
     {"belongsToTable": ["TblCoreCustomer"]},
     {"fieldName": "REG_ADDR", "fieldType": "VARCHAR(200)", "fieldNullable": True}),

    ("SourceField", "SF_AcctNo", "账号", "核心账户表的账号字段。",
     {"belongsToTable": ["TblCoreAccount"]},
     {"fieldName": "ACCT_NO", "fieldType": "VARCHAR(32)", "fieldNullable": False}),
    ("SourceField", "SF_AcctStatus", "账户状态", "核心账户表的账户状态代码字段。",
     {"belongsToTable": ["TblCoreAccount"]},
     {"fieldName": "ACCT_STS", "fieldType": "CHAR(1)", "fieldNullable": False}),
    ("SourceField", "SF_AcctBalance", "账户余额", "核心账户表的当前余额字段。",
     {"belongsToTable": ["TblCoreAccount"]},
     {"fieldName": "BAL", "fieldType": "DECIMAL(18,2)", "fieldNullable": True}),
    ("SourceField", "SF_AcctOpenDate", "开户日期", "核心账户表的开户日期字段。",
     {"belongsToTable": ["TblCoreAccount"]},
     {"fieldName": "OPEN_DATE", "fieldType": "DATE", "fieldNullable": False}),

    ("SourceField", "SF_TxnAmt", "交易金额", "核心交易流水表的发生额字段。",
     {"belongsToTable": ["TblCoreTransaction"]},
     {"fieldName": "TXN_AMT", "fieldType": "DECIMAL(18,2)", "fieldNullable": False}),
    ("SourceField", "SF_DrCrFlag", "借贷标志", "核心交易流水表的借贷方向标识字段。",
     {"belongsToTable": ["TblCoreTransaction"]},
     {"fieldName": "DR_CR_FLAG", "fieldType": "CHAR(1)", "fieldNullable": False}),

    # 字段映射条目：六种转换类型各至少一例，另含一条「未映射」以演示覆盖率校验
    ("FieldMapping", "MapCustomerCode", "客户编号映射", "客户主题域客户编号字段的取数映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_CustNo"],
      "usesTransformationRule": ["RuleDirect"]},
     {"mappingCode": "M-EAST-CUS-001", "targetOntologyProperty": "eastCustomerCode",
      "targetDomainClass": "EASTCustomerItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_CUSTOMER", "sourceFieldCode": "CUST_NO",
      "sourceFieldType": "VARCHAR(20)", "transformationType": "直接映射",
      "transformationExpression": "target = CUST_NO", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "官方数据项编号待规范下发后回填。"}),
    ("FieldMapping", "MapCustomerName", "客户名称映射", "客户主题域客户名称字段的取数映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_CustName"],
      "usesTransformationRule": ["RuleDirect"]},
     {"mappingCode": "M-EAST-CUS-002", "targetOntologyProperty": "eastCustomerName",
      "targetDomainClass": "EASTCustomerItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_CUSTOMER", "sourceFieldCode": "CUST_NAME",
      "sourceFieldType": "VARCHAR(200)", "transformationType": "直接映射",
      "transformationExpression": "target = CUST_NAME", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "官方数据项编号待规范下发后回填。"}),
    ("FieldMapping", "MapIdType", "证件类型映射", "客户主题域证件类型字段的代码转换映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_IdType"],
      "usesTransformationRule": ["RuleCodeConversion"],
      "usesCodeMapping": ["CodeMapIdType"]},
     {"mappingCode": "M-EAST-CUS-003", "targetOntologyProperty": "eastIdType",
      "targetDomainClass": "EASTCustomerItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_CUSTOMER", "sourceFieldCode": "ID_TYPE",
      "sourceFieldType": "CHAR(2)", "transformationType": "代码转换",
      "transformationExpression": "target = codeMap[ID_TYPE]", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "完整代码表须以官方规范为准，当前仅示例一档。"}),
    ("FieldMapping", "MapCustomerType", "客户类型映射", "客户主题域客户类型字段的条件分支映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_CustType"],
      "usesTransformationRule": ["RuleConditional"]},
     {"mappingCode": "M-EAST-CUS-004", "targetOntologyProperty": "eastCustomerType",
      "targetDomainClass": "EASTCustomerItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_CUSTOMER", "sourceFieldCode": "CUST_KIND",
      "sourceFieldType": "CHAR(1)", "transformationType": "条件分支",
      "transformationExpression": "target = (CUST_KIND == 'C') ? '对公客户' : '对私客户'",
      "isRequired": True, "mappingStatus": "待确认", "mappingConfidence": "拟定",
      "mappingNote": "对公对私分类粒度须对照官方口径确认。"}),
    ("FieldMapping", "MapRegisterAddress", "注册地址映射", "客户主题域注册地址字段的拼接映射。",
     {"inSpecification": ["SpecEAST2026Q3"],
      "usesTransformationRule": ["RuleConcat"]},
     {"mappingCode": "M-EAST-CUS-005", "targetOntologyProperty": "eastRegisterAddress",
      "targetDomainClass": "EASTCustomerItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_CUSTOMER", "sourceFieldCode": "REG_PROV+REG_CITY+REG_ADDR",
      "sourceFieldType": "VARCHAR(280)", "transformationType": "字符串拼接",
      "transformationExpression": "target = REG_PROV + REG_CITY + REG_ADDR",
      "isRequired": False, "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "多源字段映射，故不设 mapsSourceField，来源记于表达式。"}),
    ("FieldMapping", "MapIndustryCode", "行业代码映射（未映射）", "客户主题域行业代码字段尚未确定取数来源。",
     {"inSpecification": ["SpecEAST2026Q3"]},
     {"mappingCode": "M-EAST-CUS-006", "targetOntologyProperty": "eastIndustryCode",
      "targetDomainClass": "EASTCustomerItem", "transformationType": "直接映射",
      "isRequired": True, "mappingStatus": "未映射", "mappingConfidence": "拟定",
      "mappingNote": "源字段待数据字典梳理后补充；该条目用于演示覆盖率校验。"}),

    ("FieldMapping", "MapAccountNo", "账号映射", "账户主题域账号字段的取数映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_AcctNo"],
      "usesTransformationRule": ["RuleDirect"]},
     {"mappingCode": "M-EAST-ACC-001", "targetOntologyProperty": "eastAccountNo",
      "targetDomainClass": "EASTAccountItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_ACCOUNT", "sourceFieldCode": "ACCT_NO",
      "sourceFieldType": "VARCHAR(32)", "transformationType": "直接映射",
      "transformationExpression": "target = ACCT_NO", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "官方数据项编号待规范下发后回填。"}),
    ("FieldMapping", "MapAccountStatus", "账户状态映射", "账户主题域账户状态字段的代码转换映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_AcctStatus"],
      "usesTransformationRule": ["RuleCodeConversion"],
      "usesCodeMapping": ["CodeMapAcctStatus"]},
     {"mappingCode": "M-EAST-ACC-002", "targetOntologyProperty": "eastAccountStatus",
      "targetDomainClass": "EASTAccountItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_ACCOUNT", "sourceFieldCode": "ACCT_STS",
      "sourceFieldType": "CHAR(1)", "transformationType": "代码转换",
      "transformationExpression": "target = codeMap[ACCT_STS]", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "完整状态代码表须以官方规范为准。"}),
    ("FieldMapping", "MapAccountBalance", "账户余额映射", "账户主题域账户余额字段的取数映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_AcctBalance"],
      "usesTransformationRule": ["RuleDirect"]},
     {"mappingCode": "M-EAST-ACC-003", "targetOntologyProperty": "eastAccountBalance",
      "targetDomainClass": "EASTAccountItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_ACCOUNT", "sourceFieldCode": "BAL",
      "sourceFieldType": "DECIMAL(18,2)", "transformationType": "直接映射",
      "transformationExpression": "target = BAL", "defaultValue": "0.00",
      "isRequired": True, "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "余额为报送时点快照值，须按快照时点取数。"}),
    ("FieldMapping", "MapOpenDate", "开户日期映射", "账户主题域开户日期字段的计算派生映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_AcctOpenDate"],
      "usesTransformationRule": ["RuleComputed"]},
     {"mappingCode": "M-EAST-ACC-004", "targetOntologyProperty": "eastOpenDate",
      "targetDomainClass": "EASTAccountItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_ACCOUNT", "sourceFieldCode": "OPEN_DATE",
      "sourceFieldType": "DATE", "transformationType": "计算派生",
      "transformationExpression": "target = format(OPEN_DATE, 'yyyy-MM-dd')",
      "isRequired": True, "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "源为 DATE 类型，报送口径为定长文本日期。"}),
    ("FieldMapping", "MapAccountCurrency", "账户币种映射", "账户主题域账户币种字段的常量映射。",
     {"inSpecification": ["SpecEAST2026Q3"],
      "usesTransformationRule": ["RuleConstant"]},
     {"mappingCode": "M-EAST-ACC-005", "targetOntologyProperty": "eastAccountCurrency",
      "targetDomainClass": "EASTAccountItem", "transformationType": "常量赋值",
      "transformationExpression": "target = 'CNY'", "defaultValue": "CNY",
      "isRequired": True, "mappingStatus": "待确认", "mappingConfidence": "拟定",
      "mappingNote": "当前仅人民币账户；若开立外币账户须改为取数映射。"}),

    ("FieldMapping", "MapTxnAmount", "交易金额映射", "交易主题域交易金额字段的取数映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_TxnAmt"],
      "usesTransformationRule": ["RuleDirect"]},
     {"mappingCode": "M-EAST-TXN-001", "targetOntologyProperty": "eastTxnAmount",
      "targetDomainClass": "EASTTransactionItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_TXN_JOURNAL", "sourceFieldCode": "TXN_AMT",
      "sourceFieldType": "DECIMAL(18,2)", "transformationType": "直接映射",
      "transformationExpression": "target = TXN_AMT", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "官方数据项编号待规范下发后回填。"}),
    ("FieldMapping", "MapTxnDirection", "交易方向映射", "交易主题域交易方向字段的代码转换映射。",
     {"inSpecification": ["SpecEAST2026Q3"], "mapsSourceField": ["SF_DrCrFlag"],
      "usesTransformationRule": ["RuleCodeConversion"],
      "usesCodeMapping": ["CodeMapDrCr"]},
     {"mappingCode": "M-EAST-TXN-002", "targetOntologyProperty": "eastTxnDirection",
      "targetDomainClass": "EASTTransactionItem", "sourceSystemName": "核心业务系统",
      "sourceTableCode": "CB_TXN_JOURNAL", "sourceFieldCode": "DR_CR_FLAG",
      "sourceFieldType": "CHAR(1)", "transformationType": "代码转换",
      "transformationExpression": "target = codeMap[DR_CR_FLAG]", "isRequired": True,
      "mappingStatus": "已确认", "mappingConfidence": "拟定",
      "mappingNote": "借贷标志与报送口径方向的对应关系须以官方规范为准。"}),

    # --- 机构层级与岗位实例 ---
    ("SubBranch", "OrgSubBranchPudong", "浦东支行", "隶属于上海分行、直接面向客户经营的支行。",
     {"subOrganizationOf": ["OrgBranchShanghai"]},
     {"organizationCode": "ORG3101-01", "organizationLevel": "支行"}),
    ("Outlet", "OrgOutletLujiazui", "陆家嘴网点", "对外办理柜面业务的营业网点。",
     {"subOrganizationOf": ["OrgSubBranchPudong"]},
     {"organizationCode": "ORG3101-01-01", "organizationLevel": "网点"}),
    ("Department", "DeptRiskManagement", "风险管理部", "总行内设的风险管理职能部门。",
     {"subOrganizationOf": ["OrgHeadOffice"]},
     {"organizationCode": "DEPT-RM", "organizationLevel": "总行部门"}),
    ("Position", "PosTeller", "柜员岗", "办理柜面存取款与结算业务的岗位。",
     {"positionRequiresRole": ["RoleBusinessOperator"]},
     {"positionCode": "P-TEL", "positionTitle": "柜员"}),
    ("Position", "PosLoanOfficer", "信贷经理岗", "负责授信调查与贷款发放的岗位。",
     {"positionRequiresRole": ["RoleBusinessOperator"]},
     {"positionCode": "P-LO", "positionTitle": "信贷经理"}),
    ("Position", "PosAuditor", "审计岗", "负责日志审计与合规检查的岗位。",
     {"positionRequiresRole": ["RoleAuditor"]},
     {"positionCode": "P-AUD", "positionTitle": "审计员"}),
    ("Position", "PosSystemAdmin", "系统管理岗", "负责系统参数配置与账号管理的岗位。",
     {"positionRequiresRole": ["RoleSystemAdmin"]},
     {"positionCode": "P-SA", "positionTitle": "系统管理员"}),
    ("Position", "PosSupervisor", "监督岗", "负责业务监督与违规处置的岗位。",
     {"positionRequiresRole": ["RoleSupervisor"]},
     {"positionCode": "P-SUP", "positionTitle": "监督员"}),

    # --- 会计账务实例 ---
    ("AssetSubject", "SubjectCash", "现金及存放中央银行款项", "资产类科目，核算现金及存放中央银行款项。",
     {}, {"subjectCode": "1001", "subjectName": "现金及存放中央银行款项", "balanceDirection": "借"}),
    ("AssetSubject", "SubjectLoan", "发放贷款及垫款", "资产类科目，核算发放的各项贷款。",
     {}, {"subjectCode": "1101", "subjectName": "发放贷款及垫款", "balanceDirection": "借"}),
    ("LiabilitySubject", "SubjectDeposit", "吸收存款", "负债类科目，核算吸收的各项存款。",
     {}, {"subjectCode": "2001", "subjectName": "吸收存款", "balanceDirection": "贷"}),
    ("IncomeSubject", "SubjectInterestIncome", "利息收入", "损益类收入科目，核算利息收入。",
     {}, {"subjectCode": "6011", "subjectName": "利息收入", "balanceDirection": "贷"}),
    ("AccountingPeriod", "Period2026Q3", "2026 年第三季度会计期间", "2026 年第三季度的账务核算期间。",
     {}, {"periodCode": "2026Q3", "periodStartDate": "2026-07-01",
          "periodEndDate": "2026-09-30", "periodStatus": "已结账"}),
    ("AccountingVoucher", "Voucher202609001", "2026年9月记账凭证", "华兴机械现金存入的记账凭证。",
     {"inPeriod": ["Period2026Q3"]},
     {"voucherNo": "V202609001", "accountingDate": "2026-09-01"}),
    ("AccountingEntry", "Entry202609001", "现金存入分录", "华兴机械现金存入 50 万元的借贷分录。",
     {"debitSubject": ["SubjectCash"], "creditSubject": ["SubjectDeposit"],
      "inVoucher": ["Voucher202609001"], "affectsAccount": ["AccHuaxingSettle"]},
     {"entryAmount": 500000.00, "entrySummary": "华兴机械经营回笼资金存入"}),

    # --- 担保实例 ---
    ("CorporateGuarantor", "GuarantorHengxin", "恒信集团（法人担保人）",
     "为华兴机械流动资金贷款提供连带责任保证的法人。", {}, {"guarantorIdentifier": "G0001"}),
    ("MortgageContract", "MortgageHuaxing", "华兴厂房抵押合同",
     "以华兴机械厂房为流动资金贷款提供抵押担保。",
     {"secures": ["CollHuaxingPlant"], "underGuarantee": ["AccHuaxingLoan"]},
     {"guaranteeContractNo": "MC-2026-001", "guaranteeAmount": 68000000.00, "guaranteeMethod": "抵押"}),
    ("SuretyshipContract", "SuretyHengxin", "恒信集团保证合同",
     "恒信集团为华兴机械贷款提供连带责任保证，不涉及特定押品。",
     {"underGuarantee": ["AccHuaxingLoan"]},
     {"guaranteeContractNo": "SC-2026-001", "guaranteeAmount": 20000000.00, "guaranteeMethod": "保证"}),

    # --- 定价与利率实例 ---
    ("BenchmarkRate", "RateLPR1Y", "1 年期 LPR", "贷款市场报价利率 1 年期。",
     {}, {"rateCode": "LPR-1Y", "rateValue": 3.45, "rateType": "年利率",
          "effectiveDate": "2026-08-20", "benchmarkRateName": "LPR"}),
    ("ExecutingRate", "RateHuaxingLoan", "华兴贷款执行利率", "华兴机械流动资金贷款实际执行的年利率。",
     {"basedOnBenchmark": ["RateLPR1Y"]},
     {"rateCode": "EXE-HX-001", "rateValue": 4.35, "rateType": "年利率",
      "effectiveDate": "2026-07-01", "floatingMode": "浮动", "floatingBasisPoint": 90.0}),
    ("FeeSchedule", "Schedule2026", "2026 版服务价目表", "2026 年生效的服务收费价目表。",
     {}, {"scheduleVersion": "2026"}),
    ("FeeItem", "FeeTransfer", "转账手续费", "行内转账服务的收费项目。",
     {"inFeeSchedule": ["Schedule2026"]},
     {"feeItemCode": "F-TRF", "feeRate": 0.001, "feeBasis": "按比例"}),

    # --- 反洗钱实例 ---
    ("CustomerRiskLevel", "RiskLevelMedium", "中风险", "反洗钱口径下的中风险等级。",
     {}, {"riskLevelCode": "M", "riskLevelName": "中风险", "riskLevelAssessDate": "2026-07-15"}),
    ("StandardDueDiligence", "DDHuaxing", "华兴机械标准尽职调查", "对华兴机械开展的标准尽职调查。",
     {}, {"dueDiligenceDate": "2026-07-15", "dueDiligenceResult": "通过"}),
    ("SanctionsScreening", "ScreeningHuaxing", "华兴机械制裁名单筛查", "对华兴机械开展的制裁名单比对筛查。",
     {}, {"screeningResult": "无命中", "screeningDate": "2026-09-30", "screeningListName": "联合国制裁名单"}),
    ("SanctionsScreening", "ScreeningRemitOut", "跨境汇款对手制裁筛查",
     "对跨境汇出交易对手开展的制裁名单筛查，疑似命中有待人工甄别。",
     {}, {"screeningResult": "疑似命中", "screeningDate": "2026-09-28",
          "screeningListName": "OFAC 特别指定国民名单"}),

    # --- 资本计量实例 ---
    ("RiskWeightedAsset", "RWA2026Q3", "2026Q3 风险加权资产", "2026 年第三季度末的风险加权资产。",
     {}, {"riskWeight": 100.0, "weightedAssetAmount": 12500000000.00}),
    ("CapitalAdequacy", "CapitalAdequacy2026Q3", "2026Q3 资本充足率计量", "2026 年第三季度末资本充足率测算结果。",
     {"basedOnRWA": ["RWA2026Q3"]}, {"capitalRatio": 13.85, "tierOneRatio": 11.20}),
    ("LoanLossProvision", "ProvisionHuaxing", "华兴贷款损失准备", "针对华兴机械贷款计提的损失准备。",
     {}, {"provisionAmount": 1250000.00, "provisionRatio": 2.50}),
    ("CreditExposure", "ExposureHuaxing", "华兴机械信用风险敞口", "对华兴机械的信用风险暴露金额。",
     {"mitigatedBy": ["MitigationHuaxingPlant"]}, {"exposureAmount": 50000000.00}),
    ("RiskMitigation", "MitigationHuaxingPlant", "厂房抵押缓释", "以厂房抵押降低信用风险敞口的缓释安排。",
     {}, {"mitigationType": "押品"}),
    ("Impairment", "ImpairmentHuaxing", "华兴贷款减值", "华兴机械贷款按预期信用损失模型确认的减值。",
     {"impairs": ["AccHuaxingLoan"]}, {"impairmentAmount": 320000.00, "impairmentStage": "第二阶段"}),

    # --- 运营与清算实例 ---
    ("BatchJob", "BatchJobDaily20260930", "2026-09-30 日终批处理", "季度末日终结息与账务加工批处理作业。",
     {"executedOn": ["CompDatabase"], "producesError": ["ErrorTransfer001"]},
     {"batchJobCode": "EOD-20260930", "batchJobStatus": "成功",
      "batchStartTime": "2026-09-30T22:00:00", "batchEndTime": "2026-09-30T23:30:00"}),
    ("Reconciliation", "Recon20260930", "2026-09-30 账务对账", "总账与分户账的季度末勾稽核对。",
     {"reconcilesAccount": ["AccHuaxingSettle"]}, {"reconStatus": "相符", "reconDifference": 0.0}),
    ("SettlementSession", "Session20260930", "2026-09-30 清算场次", "季度末支付系统清算场次。",
     {}, {"sessionNo": "SS-20260930", "sessionTime": "2026-09-30T17:00:00"}),
    ("OperationalError", "ErrorTransfer001", "批量代扣金额差错", "日终批处理中发现的待更正差错。",
     {}, {"errorCode": "E-2026-0901", "errorStatus": "待更正"}),
]


def build(out_path: str, iri: str | None = None) -> str:
    """按上述定义构建本体并写入 out_path，返回文件路径。"""
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ontology_core import (  # noqa: E402
        DEFAULT_IRI,
        add_class,
        add_data_property,
        add_disjoint,
        add_individual,
        add_object_property,
        add_restriction,
        create,
        save,
    )

    if os.path.exists(out_path):
        os.remove(out_path)
    onto = create(out_path, iri or DEFAULT_IRI)

    for name, parent, *_ in CLASSES:
        add_class(onto, name, parent)

    for name, _parent, label, comment in CLASSES:
        cls = getattr(onto, name)
        with onto:
            if label:
                cls.label.append(label)
            if comment:
                cls.comment.append(comment)

    for group in DISJOINT_GROUPS:
        add_disjoint(onto, group)

    for name, domain, rng, chars, _inv, label, comment in OBJECT_PROPERTIES:
        add_object_property(onto, name, domain, rng, chars, None, label, comment)

    for name, domain, rt, func, label, comment in DATA_PROPERTIES:
        add_data_property(onto, name, domain, rt, func, label, comment)

    for cls_name, prop, kind, target, card in RESTRICTIONS:
        add_restriction(onto, cls_name, prop, kind, target, card)

    from owlready2 import Imp  # noqa: E402

    with onto:
        for _rule_name, body in SWRL_RULES:
            rule = Imp()
            rule.set_as_rule(body)

    # 两阶段：先创建全部个体，再建立相互引用，避免前向引用失败
    created = {}
    for cls_name, name, label, comment, _rels, _vals in INDIVIDUALS:
        created[name] = add_individual(onto, cls_name, name, label, comment)

    from owlready2 import FunctionalProperty  # noqa: E402

    with onto:
        for _cls_name, name, _label, _comment, rels, vals in INDIVIDUALS:
            ind = created[name]
            for prop_name, targets in (rels or {}).items():
                prop = getattr(onto, prop_name, None)
                # 函数性属性返回单值、不支持 append，必须走赋值；否则用 append 累加
                functional = prop is not None and FunctionalProperty in prop.is_a
                for t in targets:
                    if functional:
                        setattr(ind, prop_name, created[t])
                    else:
                        getattr(ind, prop_name).append(created[t])
            for prop_name, value in (vals or {}).items():
                setattr(ind, prop_name, value)

    # 从「角色互斥类组」自动派生个体级 separatedFrom。
    # 手工逐对声明极易遗漏（曾漏掉 业务操作权×审计权 这类关键组合），
    # 改为由互斥类组推导，新增角色个体时也会自动完备。
    with onto:
        for group in DISJOINT_GROUPS:
            classes = [getattr(onto, n, None) for n in group]
            classes = [c for c in classes if c is not None]
            if len(classes) < 2 or not all(issubclass(c, onto.Role) for c in classes):
                continue
            inds = []
            for c in classes:
                inds.extend(list(c.instances()))
            for i, a in enumerate(inds):
                for b in inds[i + 1:]:
                    if b not in a.separatedFrom:
                        a.separatedFrom.append(b)

    save(onto, out_path)
    return out_path
