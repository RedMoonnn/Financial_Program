
// 中文多级表单映射
export const cascaderOptions = [
    {
        label: '个股资金流',
        value: 'Stock_Flow',
        children: [
            {
                label: '全部A股', value: 'All_Stocks',
                children: [
                    { label: '今日', value: 'Today' },
                    { label: '3日', value: '3_Day' },
                    { label: '5日', value: '5_Day' },
                    { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '沪深A股', value: 'SH&SZ_A_Shares', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '沪市A股', value: 'SH_A_Shares', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '科创板', value: 'STAR_Market', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '深市A股', value: 'SZ_A_Shares', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '创业板', value: 'ChiNext_Market', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '沪市B股', value: 'SH_B_Shares', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '深市B股', value: 'SZ_B_Shares', children: [
                    { label: '今日', value: 'Today' }, { label: '3日', value: '3_Day' }, { label: '5日', value: '5_Day' }, { label: '10日', value: '10_Day' },
                ]
            },
        ]
    },
    {
        label: '板块资金流',
        value: 'Sector_Flow',
        children: [
            {
                label: '行业板块', value: 'Industry_Flow',
                children: [
                    { label: '今日', value: 'Today' },
                    { label: '3日', value: '3_Day' },
                    { label: '5日', value: '5_Day' },
                    { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '概念板块', value: 'Concept_Flow',
                children: [
                    { label: '今日', value: 'Today' },
                    { label: '3日', value: '3_Day' },
                    { label: '5日', value: '5_Day' },
                    { label: '10日', value: '10_Day' },
                ]
            },
            {
                label: '区域板块', value: 'Regional_Flow',
                children: [
                    { label: '今日', value: 'Today' },
                    { label: '3日', value: '3_Day' },
                    { label: '5日', value: '5_Day' },
                    { label: '10日', value: '10_Day' },
                ]
            },
        ]
    }
];
